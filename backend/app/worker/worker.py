from sqlalchemy import text

from app.db.session import SessionLocal
from app.services.mock_provider import mock_generate
from app.services.openai_image_adapter import OpenAIImageAdapter, json_dumps_safe


def process_task(task_id: int):
    db = SessionLocal()
    row = db.execute(
        text("SELECT id, task_type, payload, provider, request_params FROM generation_tasks WHERE id=:id"),
        {"id": task_id},
    ).fetchone()
    if not row:
        db.close()
        return

    try:
        if row.provider == "openai":
            adapter = OpenAIImageAdapter()
            req = row.request_params
            import json
            req_data = json.loads(req) if req else {}
            if row.task_type == "image_generate":
                data = adapter.generate(
                    prompt=req_data.get("prompt", row.payload),
                    size=req_data.get("size", "1024x1024"),
                    quality=req_data.get("quality", "standard"),
                )
            elif row.task_type == "image_edit":
                data = adapter.edit(
                    prompt=req_data.get("prompt", row.payload),
                    image_base64=req_data.get("image_base64", ""),
                    mask_base64=req_data.get("mask_base64"),
                    size=req_data.get("size", "1024x1024"),
                )
            else:
                raise ValueError(f"unsupported openai task_type: {row.task_type}")

            db.execute(
                text("""
                    UPDATE generation_tasks
                    SET status='done',
                        result=:result,
                        response_payload=:response_payload,
                        cost_estimate=:cost_estimate,
                        error_reason=''
                    WHERE id=:id
                """),
                {
                    "id": task_id,
                    "result": json_dumps_safe(data),
                    "response_payload": json_dumps_safe(data.get("response", {})),
                    "cost_estimate": data.get("cost_estimate", 0),
                },
            )
        else:
            result = mock_generate(row.task_type, row.payload)
            db.execute(
                text("UPDATE generation_tasks SET status='done', result=:result WHERE id=:id"),
                {"id": task_id, "result": result},
            )

        db.commit()
    except Exception as e:
        db.execute(
            text("UPDATE generation_tasks SET status='failed', error_reason=:error_reason WHERE id=:id"),
            {"id": task_id, "error_reason": str(e)},
        )
        db.commit()
    finally:
        db.close()

import json
from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from rq import Queue
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.common import SimpleCreate, TaskCreate
from app.schemas.shots import ShotCreate, ShotUpdate
from app.schemas.generation import OpenAIImageGenerateRequest, OpenAIImageEditRequest
from app.worker.worker import process_task

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {"ok": True}

@router.post("/projects")
def create_project(payload: SimpleCreate, db: Session = Depends(get_db)):
    db.execute(text("INSERT INTO projects(name, description) VALUES(:name,:description)"), payload.model_dump())
    db.commit()
    return {"message": "created"}

@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM projects ORDER BY id DESC")).mappings().all()
    return rows

@router.get("/assets")
def list_assets(db: Session = Depends(get_db)):
    return db.execute(text("SELECT * FROM assets ORDER BY id DESC")).mappings().all()



@router.post("/assets")
def create_asset(payload: dict, db: Session = Depends(get_db)):
    params = {
        "project_id": payload.get("project_id"),
        "task_id": payload.get("task_id"),
        "asset_type": payload.get("asset_type", "mock"),
        "provider": payload.get("provider", "manual"),
        "title": payload.get("title", ""),
        "description": payload.get("description", ""),
        "url": payload.get("url", ""),
        "local_path": payload.get("local_path", ""),
        "thumbnail_url": payload.get("thumbnail_url", ""),
        "prompt": payload.get("prompt", ""),
        "negative_prompt": payload.get("negative_prompt", ""),
        "metadata": payload.get("metadata", ""),
        "status": payload.get("status", "draft"),
    }
    row = db.execute(text("""
        INSERT INTO assets(project_id, task_id, asset_type, provider, title, description, url, local_path, thumbnail_url, prompt, negative_prompt, metadata, status)
        VALUES(:project_id, :task_id, :asset_type, :provider, :title, :description, :url, :local_path, :thumbnail_url, :prompt, :negative_prompt, :metadata, :status)
        RETURNING *
    """), params).mappings().fetchone()
    db.commit()
    return dict(row)


@router.post("/tasks/{task_id}/create-asset")
def create_asset_from_task(task_id: int, db: Session = Depends(get_db)):
    task = db.execute(text("""
        SELECT id, task_type, provider, payload, result, request_params, response_payload, cost_estimate
        FROM generation_tasks
        WHERE id=:id
    """), {"id": task_id}).mappings().fetchone()

    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    asset_type = "mock"
    if task["task_type"] == "image_generate":
        asset_type = "image"
    elif task["task_type"] == "video_generate":
        asset_type = "video"

    metadata = json.dumps({
        "task_result": task["result"],
        "response_payload": task["response_payload"],
        "request_params": task["request_params"],
        "cost_estimate": str(task["cost_estimate"]) if task["cost_estimate"] is not None else None
    }, ensure_ascii=False)

    row = db.execute(text("""
        INSERT INTO assets(project_id, task_id, asset_type, provider, title, description, url, local_path, thumbnail_url, prompt, negative_prompt, metadata, status)
        VALUES(NULL, :task_id, :asset_type, :provider, :title, '', '', '', '', :prompt, '', :metadata, 'ready')
        RETURNING *
    """), {
        "task_id": task_id,
        "asset_type": asset_type,
        "provider": task["provider"] or "mock",
        "title": f"Task #{task_id} Asset",
        "prompt": task["payload"] or "",
        "metadata": metadata,
    }).mappings().fetchone()
    db.commit()
    return dict(row)
@router.post("/tasks/mock-generate")
def mock_task(payload: TaskCreate, db: Session = Depends(get_db)):
    row = db.execute(text("INSERT INTO generation_tasks(task_type, payload, status, result) VALUES(:task_type,:payload,'queued','') RETURNING id"), payload.model_dump()).fetchone()
    db.commit()
    q = Queue("default", connection=Redis.from_url(settings.redis_url))
    q.enqueue(process_task, row.id)
    return {"task_id": row.id, "status": "queued"}



@router.post("/tasks/openai-image-generate")
def openai_image_generate(payload: OpenAIImageGenerateRequest, db: Session = Depends(get_db)):
    params = payload.model_dump_json()
    row = db.execute(text("""
        INSERT INTO generation_tasks(task_type, payload, status, result, provider, request_params, response_payload, cost_estimate, error_reason)
        VALUES('image_generate', :payload, 'queued', '', 'openai', :request_params, '', 0, '')
        RETURNING id
    """), {"payload": payload.prompt, "request_params": params}).fetchone()
    db.commit()
    q = Queue("default", connection=Redis.from_url(settings.redis_url))
    q.enqueue(process_task, row.id)
    return {"task_id": row.id, "status": "queued"}


@router.post("/tasks/openai-image-edit")
def openai_image_edit(payload: OpenAIImageEditRequest, db: Session = Depends(get_db)):
    params = payload.model_dump_json()
    row = db.execute(text("""
        INSERT INTO generation_tasks(task_type, payload, status, result, provider, request_params, response_payload, cost_estimate, error_reason)
        VALUES('image_edit', :payload, 'queued', '', 'openai', :request_params, '', 0, '')
        RETURNING id
    """), {"payload": payload.prompt, "request_params": params}).fetchone()
    db.commit()
    q = Queue("default", connection=Redis.from_url(settings.redis_url))
    q.enqueue(process_task, row.id)
    return {"task_id": row.id, "status": "queued"}

@router.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.execute(text("SELECT * FROM generation_tasks ORDER BY id DESC")).mappings().all()


@router.get("/shots")
def list_shots(db: Session = Depends(get_db)):
    return db.execute(text("SELECT * FROM shots ORDER BY id DESC")).mappings().all()


@router.post("/shots")
def create_shot(payload: ShotCreate, db: Session = Depends(get_db)):
    params = payload.model_dump()
    row = db.execute(text("""
        INSERT INTO shots(episode, scene_no, shot_no, duration_sec, aspect_ratio, shot_size, camera_angle, action, dialogue, visual_requirements, negative_prompt, status)
        VALUES(:episode, :scene_no, :shot_no, :duration_sec, :aspect_ratio, :shot_size, :camera_angle, :action, :dialogue, :visual_requirements, :negative_prompt, :status)
        RETURNING id
    """), params).fetchone()
    db.commit()
    return {"id": row.id}


@router.put("/shots/{shot_id}")
def update_shot(shot_id: int, payload: ShotUpdate, db: Session = Depends(get_db)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        return {"message": "no fields to update"}

    sets = ", ".join([f"{k}=:{k}" for k in data.keys()])
    data["id"] = shot_id
    db.execute(text(f"UPDATE shots SET {sets} WHERE id=:id"), data)
    db.commit()
    return {"message": "updated"}


@router.delete("/shots/{shot_id}")
def delete_shot(shot_id: int, db: Session = Depends(get_db)):
    db.execute(text("DELETE FROM shots WHERE id=:id"), {"id": shot_id})
    db.commit()
    return {"message": "deleted"}

import json
import random


def mock_generate(task_type: str, payload: str) -> str:
    data = {
        "task_type": task_type,
        "payload": payload,
        "output": f"mock_{task_type}_{random.randint(1000,9999)}",
        "meta": {"provider": "mock-provider", "quality": "preview"}
    }
    return json.dumps(data, ensure_ascii=False)

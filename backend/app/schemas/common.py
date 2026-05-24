from pydantic import BaseModel


class SimpleCreate(BaseModel):
    name: str
    description: str | None = ""


class TaskCreate(BaseModel):
    task_type: str
    payload: str

from pydantic import BaseModel


class ShotBase(BaseModel):
    episode: int
    scene_no: str
    shot_no: str
    duration_sec: int
    aspect_ratio: str
    shot_size: str
    camera_angle: str
    action: str = ""
    dialogue: str = ""
    visual_requirements: str = ""
    negative_prompt: str = ""
    status: str = "draft"


class ShotCreate(ShotBase):
    pass


class ShotUpdate(BaseModel):
    episode: int | None = None
    scene_no: str | None = None
    shot_no: str | None = None
    duration_sec: int | None = None
    aspect_ratio: str | None = None
    shot_size: str | None = None
    camera_angle: str | None = None
    action: str | None = None
    dialogue: str | None = None
    visual_requirements: str | None = None
    negative_prompt: str | None = None
    status: str | None = None

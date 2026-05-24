from pydantic import BaseModel


class OpenAIImageGenerateRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"


class OpenAIImageEditRequest(BaseModel):
    prompt: str
    image_base64: str
    mask_base64: str | None = None
    size: str = "1024x1024"

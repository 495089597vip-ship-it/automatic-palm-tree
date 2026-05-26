import base64
from enum import Enum

from pydantic import BaseModel, Field, field_validator


MAX_BASE64_LENGTH = 20 * 1024 * 1024  # 20MB encoded input safety cap


class ImageSize(str, Enum):
    s1024 = "1024x1024"
    s1536x1024 = "1536x1024"
    s1024x1536 = "1024x1536"


class ImageQuality(str, Enum):
    standard = "standard"
    high = "high"


class OpenAIImageGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    size: ImageSize = ImageSize.s1024
    quality: ImageQuality = ImageQuality.standard


class OpenAIImageEditRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    image_base64: str
    mask_base64: str | None = None
    size: ImageSize = ImageSize.s1024

    @field_validator("image_base64", "mask_base64")
    @classmethod
    def validate_base64_payload(cls, value: str | None):
        if value is None:
            return value
        if len(value) > MAX_BASE64_LENGTH:
            raise ValueError("base64 payload too large")
        try:
            base64.b64decode(value, validate=True)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("invalid base64 payload") from exc
        return value

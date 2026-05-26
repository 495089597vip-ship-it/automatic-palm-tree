import pytest
from pydantic import ValidationError

from app.schemas.generation import OpenAIImageEditRequest, OpenAIImageGenerateRequest


def test_generate_request_rejects_invalid_size():
    with pytest.raises(ValidationError):
        OpenAIImageGenerateRequest(prompt="ok", size="512x512")


def test_edit_request_rejects_invalid_base64():
    with pytest.raises(ValidationError):
        OpenAIImageEditRequest(prompt="ok", image_base64="not-valid-base64")


def test_edit_request_accepts_valid_base64():
    req = OpenAIImageEditRequest(prompt="ok", image_base64="aGVsbG8=")
    assert req.image_base64 == "aGVsbG8="

import base64
import json
from io import BytesIO

from openai import OpenAI

from app.core.config import settings


class OpenAIImageAdapter:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> dict:
        response = self.client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            quality=quality,
        )
        return self._normalize_response(response, mode="text_to_image", prompt=prompt, size=size, quality=quality)

    def edit(self, prompt: str, image_base64: str, mask_base64: str | None = None, size: str = "1024x1024") -> dict:
        image_bytes = base64.b64decode(image_base64)
        image_file = BytesIO(image_bytes)
        image_file.name = "image.png"

        kwargs = {"model": "gpt-image-1", "prompt": prompt, "image": image_file, "size": size}
        if mask_base64:
            mask_bytes = base64.b64decode(mask_base64)
            mask_file = BytesIO(mask_bytes)
            mask_file.name = "mask.png"
            kwargs["mask"] = mask_file

        response = self.client.images.edit(**kwargs)
        return self._normalize_response(response, mode="image_edit", prompt=prompt, size=size)

    def _normalize_response(self, response, **request_meta) -> dict:
        data = []
        for item in getattr(response, "data", []) or []:
            data.append({"b64_json": getattr(item, "b64_json", None), "url": getattr(item, "url", None)})

        usage = getattr(response, "usage", None)
        usage_obj = {
            "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
            "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
            "total_tokens": getattr(usage, "total_tokens", None) if usage else None,
        }
        # simple estimate placeholder; can be replaced by pricing table later
        cost_estimate = round(((usage_obj.get("total_tokens") or 0) / 1000) * 0.01, 6)

        return {
            "request": request_meta,
            "response": {"created": getattr(response, "created", None), "data": data, "usage": usage_obj},
            "cost_estimate": cost_estimate,
        }


def json_dumps_safe(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)

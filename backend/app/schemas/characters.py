from pydantic import BaseModel


class CharacterCreate(BaseModel):
    name: str
    description: str | None = ""
    appearance: str | None = ""
    personality: str | None = ""
    reference_image_url: str | None = ""


class CharacterOut(BaseModel):
    id: int
    name: str
    description: str | None = ""
    appearance: str | None = ""
    personality: str | None = ""
    reference_image_url: str | None = ""

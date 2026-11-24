from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    token: str = Field(min_length=1, strict=True)


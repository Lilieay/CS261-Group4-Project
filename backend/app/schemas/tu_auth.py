from pydantic import BaseModel, Field


class TUVerifyRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class TUVerifyResponse(BaseModel):
    verified: bool
    message: str
    source: str

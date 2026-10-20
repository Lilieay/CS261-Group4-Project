from pydantic import BaseModel


class MyGuideDeleteResponse(BaseModel):
    id: int
    message: str

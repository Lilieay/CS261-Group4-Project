from pydantic import BaseModel


class SavedGuideState(BaseModel):
    id: int
    saved: bool

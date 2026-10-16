from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=100)


class UserDTO(BaseModel):
    id: int
    username: str
    display_name: str
    role: str


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user: UserDTO


class LoginStatusResponse(BaseModel):
    logged_in: bool
    user: UserDTO | None = None


class MessageResponse(BaseModel):
    message: str

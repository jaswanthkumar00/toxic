from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        name = value.strip()
        if len(name) < 2:
            raise ValueError("Name must contain at least two non-whitespace characters.")
        return name


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str


class SubmissionRequest(BaseModel):
    exercise_id: int
    code: str = Field(min_length=1, max_length=30000)
    action: str = Field(default="submit", pattern="^(run|submit)$")


class HintRequest(BaseModel):
    exercise_id: int
    code: str = Field(default="", max_length=30000)
    error_message: str = Field(default="", max_length=3000)

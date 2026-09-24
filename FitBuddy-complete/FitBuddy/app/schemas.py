from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(min_length=1, max_length=120)
    user_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=500)
    goal: Goal
    intensity: Intensity

    @field_validator("username")
    @classmethod
    def username_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Username cannot be blank.")
        return value


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    feedback: str = Field(min_length=3, max_length=2000)


class UserPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    age: int
    weight: float
    goal: str
    intensity: str
    original_plan: str
    updated_plan: str | None
    nutrition_tip: str
    feedback: str | None
    created_at: str
    updated_at: str


class GenerationResponse(BaseModel):
    message: str
    plan: UserPlanResponse

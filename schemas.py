from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, validator


Priority = Literal["Low", "Medium", "High"]
Status = Literal["Pending", "In Progress", "Completed"]


class TaskCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    task_name: str = Field(..., min_length=1, max_length=200)
    priority: Priority
    deadline: date
    status: Status = "Pending"
    category: str = Field(..., min_length=1, max_length=80)
    estimated_time: float = Field(..., gt=0, le=1000)

    @validator("task_name", "category")
    def strip_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @validator("deadline")
    def deadline_must_not_be_past(cls, value):
        if value < date.today():
            raise ValueError("deadline cannot be in the past")
        return value


class TaskResponse(BaseModel):
    id: str
    user_id: str
    task_name: str
    priority: str
    deadline: date
    status: str
    category: str
    estimated_time: float
    priority_score: float
    predicted_priority: str
    created_at: str
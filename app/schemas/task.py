from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.task import TaskStatus

class TaskBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.PENDING

class TaskCreate(TaskBase):
    title: str

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    created_at: datetime
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True


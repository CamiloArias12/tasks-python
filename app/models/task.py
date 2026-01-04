from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.db.base_class import Base
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default=TaskStatus.PENDING.value, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

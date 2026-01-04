from fastapi import APIRouter, status
from app.api.v1.controllers.task_controller import TaskController
from app.schemas.task import Task as TaskSchema
from app.schemas.response import Envelope, PaginatedEnvelope

router = APIRouter()
task_controller = TaskController()

router.get("/", response_model=PaginatedEnvelope[TaskSchema])(task_controller.read_tasks)
router.post("/", response_model=Envelope[TaskSchema], status_code=status.HTTP_201_CREATED)(task_controller.create_task)
router.get("/{id}", response_model=Envelope[TaskSchema])(task_controller.read_task)
router.put("/{id}", response_model=Envelope[TaskSchema])(task_controller.update_task)
router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)(task_controller.delete_task)

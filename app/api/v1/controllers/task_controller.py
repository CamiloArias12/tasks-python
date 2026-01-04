from typing import Any
from fastapi import Depends, HTTPException, status, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate
from app.schemas.response import Envelope, Meta, PaginatedEnvelope, PaginatedData, PaginationMeta
from app.services.task_service import TaskService


class TaskController:
    def __init__(self):
        self.service = TaskService()

    async def read_tasks(
        self,
        request: Request,
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Page size"),
        current_user: User = Depends(deps.get_current_user),
    ) -> Any:
        tasks, total, pages = await self.service.get_tasks(db, current_user.id, page, size)
        
        return PaginatedEnvelope(
            data=PaginatedData(
                items=tasks,
                pagination=PaginationMeta(
                    page=page,
                    size=size,
                    total=total,
                    pages=pages
                )
            ),
            meta=Meta(request_id=getattr(request.state, "request_id", None))
        )

    async def create_task(
        self,
        request: Request,
        task_in: TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(deps.get_current_user),
    ) -> Any:
        task = await self.service.create_task(db, task_in, current_user.id)
        
        return Envelope(
            data=task,
            meta=Meta(request_id=getattr(request.state, "request_id", None))
        )

    async def read_task(
        self,
        request: Request,
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(deps.get_current_user),
    ) -> Any:
        task = await self.service.get_task(db, id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {id} not found"
            )
        
        return Envelope(
            data=task,
            meta=Meta(request_id=getattr(request.state, "request_id", None))
        )

    async def update_task(
        self,
        request: Request,
        id: int,
        task_in: TaskUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(deps.get_current_user),
    ) -> Any:
        task = await self.service.update_task(db, id, current_user.id, task_in)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {id} not found"
            )
        
        return Envelope(
            data=task,
            meta=Meta(request_id=getattr(request.state, "request_id", None))
        )

    async def delete_task(
        self,
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(deps.get_current_user),
    ) -> Response:
        deleted = await self.service.delete_task(db, id, current_user.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {id} not found"
            )
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)

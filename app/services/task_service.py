from typing import Optional, Tuple, List
from math import ceil
from datetime import datetime, timezone
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:

    async def get_tasks(
        self, db: AsyncSession, owner_id: int, page: int = 1, size: int = 10
    ) -> Tuple[List[Task], int, int]:
        skip = (page - 1) * size
        
        # Filter out soft-deleted tasks
        base_filter = (Task.owner_id == owner_id) & (Task.is_deleted == False)
        
        count_stmt = select(func.count()).select_from(Task).where(base_filter)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        stmt = (
            select(Task)
            .where(base_filter)
            .order_by(desc(Task.created_at))
            .offset(skip)
            .limit(size)
        )
        
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        
        pages = ceil(total / size) if size > 0 else 0
        
        return list(tasks), total, pages

    async def create_task(
        self, db: AsyncSession, task_in: TaskCreate, owner_id: int
    ) -> Task:
        task = Task(**task_in.model_dump(), owner_id=owner_id)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def get_task(
        self, db: AsyncSession, task_id: int, owner_id: int
    ) -> Optional[Task]:
        stmt = select(Task).where(
            Task.id == task_id, 
            Task.owner_id == owner_id,
            Task.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def update_task(
        self, db: AsyncSession, task_id: int, owner_id: int, task_in: TaskUpdate
    ) -> Optional[Task]:
        task = await self.get_task(db, task_id, owner_id)
        
        if not task:
            return None
        
        update_data = task_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        return task

    async def delete_task(
        self, db: AsyncSession, task_id: int, owner_id: int
    ) -> bool:
        task = await self.get_task(db, task_id, owner_id)
        
        if not task:
            return False
        
        # Soft delete instead of hard delete
        task.is_deleted = True
        task.deleted_at = datetime.now(timezone.utc)
        db.add(task)
        await db.commit()
        
        return True

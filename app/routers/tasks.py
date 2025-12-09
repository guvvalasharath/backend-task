from fastapi import APIRouter, Depends, HTTPException, Form
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
import sqlalchemy as sa

from app.db.base import get_db
from app.db.models import Task, TaskAssignee, TaskDependency, TaskEvent
from app.routers.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/")
async def create_task(
    title: str = Form(...),
    description: str = Form(""),
    status: str = Form("todo"),
    priority: int = Form(3),
    due_date: str | None = Form(None),
    tags: str | None = Form(None),
    parent_id: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date)
        except ValueError:
            raise HTTPException(
                400,
                "Invalid due_date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"
            )
    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=parsed_due_date,
        tags=tags,
        parent_id=parent_id,
        created_by=user.id,
    )
    db.add(task)
    await db.commit()

    event = TaskEvent(
        task_id=task.id,
        user_id=user.id,
        action="created",
        details="Task created"
    )
    db.add(event)
    await db.commit()

    return {"task_id": task.id}

@router.get("/{task_id}")
async def get_task(task_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@router.get("/")
async def list_tasks(
    status: str | None = None,
    priority: int | None = None,
    assignee: str | None = None,
    tag: str | None = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    stmt = select(Task)

    if status:
        stmt = stmt.where(Task.status == status)
    if priority:
        stmt = stmt.where(Task.priority == priority)
    if tag:
        stmt = stmt.where(Task.tags.ilike(f"%{tag}%"))
    if assignee:
        stmt = stmt.join(TaskAssignee).where(TaskAssignee.user_id == assignee)

    rows = await db.scalars(stmt)
    return list(rows)

@router.post("/bulk")
async def bulk_update(
    updates: list[dict],
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    for u in updates:
        stmt = (
            update(Task)
            .where(Task.id == u["id"])
            .values(**u["fields"])
        )
        await db.execute(stmt)

    await db.commit()
    return {"updated": len(updates)}

@router.post("/{task_id}/depends-on/{other_id}")
async def add_dependency(task_id: str, other_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if task_id == other_id:
        raise HTTPException(400, "Task cannot depend on itself")

    dep = TaskDependency(task_id=task_id, depends_on_task_id=other_id)
    db.add(dep)
    await db.commit()

    return {"message": "Dependency added"}


@router.get("/analytics/overdue")
async def overdue_tasks(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    stmt = select(Task).where(
        Task.due_date < sa.func.now(),
        Task.status != "done",
    )
    rows = await db.scalars(stmt)
    return list(rows)

@router.get("/analytics/distribution")
async def distribution(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    stmt = text("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    result = await db.execute(stmt)
    rows = result.fetchall()
    return [{"status": r[0], "count": r[1]} for r in rows]

@router.get("/{task_id}/events")
async def task_events(task_id: str, days: int = 7, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    stmt = select(TaskEvent).where(
        TaskEvent.task_id == task_id,
        TaskEvent.created_at >= sa.func.now() - sa.text(f"INTERVAL '{days} days'"),
    )

    rows = await db.scalars(stmt)
    return list(rows)

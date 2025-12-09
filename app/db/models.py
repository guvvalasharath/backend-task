import sqlalchemy as sa
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = sa.Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = sa.Column(sa.String, unique=True, nullable=False)
    password_hash = sa.Column(sa.String, nullable=False)
    full_name = sa.Column(sa.String)
    role = sa.Column(sa.String, nullable=False, default="member")
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

class Task(Base):
    __tablename__ = "tasks"
    id = sa.Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text)
    status = sa.Column(sa.String, nullable=False, default="todo")
    priority = sa.Column(sa.Integer, default=3)
    due_date = sa.Column(sa.DateTime(timezone=True))
    tags = sa.Column(sa.String)
    parent_id = sa.Column(UUID(as_uuid=False), sa.ForeignKey("tasks.id"))
    created_by = sa.Column(UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())

class TaskAssignee(Base):
    __tablename__ = "task_assignees"
    task_id = sa.Column(UUID(as_uuid=False), sa.ForeignKey("tasks.id"), primary_key=True)
    user_id = sa.Column(UUID(as_uuid=False), sa.ForeignKey("users.id"), primary_key=True)

class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    task_id = sa.Column(UUID(as_uuid=False), sa.ForeignKey("tasks.id"), primary_key=True)
    depends_on_task_id = sa.Column(UUID(as_uuid=False), sa.ForeignKey("tasks.id"), primary_key=True)

class TaskEvent(Base):
    __tablename__ = "task_events"
    id = sa.Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    task_id = sa.Column(UUID(as_uuid=False), sa.ForeignKey("tasks.id"), nullable=False)
    user_id = sa.Column(UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False)
    action = sa.Column(sa.String, nullable=False)
    details = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

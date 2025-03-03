import datetime
from typing import Any, override

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from . import db


class Todo(db.Model):
    __tablename__ = "todo"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(String(120))
    completed: Mapped[bool] = mapped_column(default=False)
    deadline_at: Mapped[datetime.datetime | None] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "deadline_at": self.deadline_at.isoformat() if self.deadline_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.created_at.isoformat(),
        }

    @override
    def __repr__(self):
        return f"<Todo {self.id} {self.title}>"

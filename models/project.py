"""Project model and its one-to-many task relationship."""

from __future__ import annotations

from datetime import date
from typing import Any


class Project:
    """Represent a project owned by one user and containing tasks."""

    _next_id = 1

    def __init__(
        self,
        title: str,
        user_id: int,
        description: str = "",
        due_date: str | None = None,
        entity_id: int | None = None,
        tasks: list[Any] | None = None,
    ) -> None:
        """Initialize a project and advance its class-level ID counter."""
        self._id = entity_id if entity_id is not None else type(self)._next_id
        type(self)._next_id = max(type(self)._next_id, self._id + 1)
        self._user_id = int(user_id)
        self.title = title
        self.description = description
        self.due_date = due_date
        self.tasks = list(tasks or [])

    @property
    def id(self) -> int:
        """Return this project's stable identifier."""
        return self._id

    @property
    def user_id(self) -> int:
        """Return the ID of the project's owner."""
        return self._user_id

    @property
    def title(self) -> str:
        """Return the project title."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Set a non-empty project title."""
        clean_value = value.strip()
        if not clean_value:
            raise ValueError("Project title cannot be empty.")
        self._title = clean_value

    @property
    def description(self) -> str:
        """Return the project description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Set the project description."""
        self._description = value.strip()

    @property
    def due_date(self) -> str | None:
        """Return the ISO-formatted due date, if set."""
        return self._due_date

    @due_date.setter
    def due_date(self, value: str | None) -> None:
        """Set an optional due date after validating its ISO format."""
        clean_value = value.strip() if value else None
        if clean_value:
            date.fromisoformat(clean_value)
        self._due_date = clean_value

    def add_task(self, task: Any) -> None:
        """Attach a task once to this project's task collection."""
        if task not in self.tasks:
            self.tasks.append(task)

    def to_dict(self) -> dict[str, Any]:
        """Return project fields and related task IDs for persistence."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "task_ids": [task.id for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, record: dict[str, Any]) -> Project:
        """Build a project from one JSON record."""
        return cls(
            title=record["title"],
            user_id=int(record["user_id"]),
            description=record.get("description", ""),
            due_date=record.get("due_date"),
            entity_id=int(record["id"]),
        )

    @classmethod
    def collection(cls, records: list[dict[str, Any]]) -> list[Project]:
        """Create a project collection from serialized records."""
        return [cls.from_dict(record) for record in records]

    def __str__(self) -> str:
        """Return a concise CLI-friendly project summary."""
        due = self.due_date or "no due date"
        return f"{self.title} (#{self.id}) | due: {due} | tasks: {len(self.tasks)}"
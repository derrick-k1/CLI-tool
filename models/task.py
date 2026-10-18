"""Task model and status validation."""

from __future__ import annotations

from typing import Any


class Task:
    """Represent a task belonging to one project."""

    STATUSES = ("todo", "in_progress", "done")
    _next_id = 1

    def __init__(
        self,
        title: str,
        project_id: int,
        status: str = "todo",
        assigned_to: str | None = None,
        entity_id: int | None = None,
    ) -> None:
        """Initialize a task and advance its class-level ID counter."""
        self._id = entity_id if entity_id is not None else type(self)._next_id
        type(self)._next_id = max(type(self)._next_id, self._id + 1)
        self._project_id = int(project_id)
        self.title = title
        self.status = status
        self.assigned_to = assigned_to

    @property
    def id(self) -> int:
        """Return this task's stable identifier."""
        return self._id

    @property
    def project_id(self) -> int:
        """Return the ID of the parent project."""
        return self._project_id

    @property
    def title(self) -> str:
        """Return the task title."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Set a non-empty task title."""
        clean_value = value.strip()
        if not clean_value:
            raise ValueError("Task title cannot be empty.")
        self._title = clean_value

    @property
    def status(self) -> str:
        """Return the task's current status."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        """Set a supported task status."""
        clean_value = value.strip().lower()
        if clean_value not in self.STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(self.STATUSES)}.")
        self._status = clean_value

    @property
    def assigned_to(self) -> str | None:
        """Return the assigned user's display name, if any."""
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value: str | None) -> None:
        """Set or clear the assigned user's display name."""
        self._assigned_to = value.strip() if value and value.strip() else None

    def to_dict(self) -> dict[str, Any]:
        """Return task fields for JSON persistence."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "status": self.status,
            "assigned_to": self.assigned_to,
        }

    @classmethod
    def from_dict(cls, record: dict[str, Any]) -> Task:
        """Build a task from one JSON record."""
        return cls(
            title=record["title"],
            project_id=int(record["project_id"]),
            status=record.get("status", "todo"),
            assigned_to=record.get("assigned_to"),
            entity_id=int(record["id"]),
        )

    @classmethod
    def collection(cls, records: list[dict[str, Any]]) -> list[Task]:
        """Create a task collection from serialized records."""
        return [cls.from_dict(record) for record in records]

    def __str__(self) -> str:
        """Return a concise CLI-friendly task summary."""
        assignee = self.assigned_to or "unassigned"
        return f"{self.title} (#{self.id}) | {self.status} | assigned to: {assignee}"
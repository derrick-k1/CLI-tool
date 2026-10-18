"""User model and its one-to-many project relationship."""

from __future__ import annotations

from typing import Any

from .person import Person


class User(Person):
    """Represent a project owner, inheriting identity fields from Person."""

    _next_id = 1

    def __init__(
        self,
        name: str,
        email: str,
        entity_id: int | None = None,
        projects: list[Any] | None = None,
    ) -> None:
        """Initialize a user and an optional collection of owned projects."""
        super().__init__(name, email, entity_id)
        self.projects = list(projects or [])

    def add_project(self, project: Any) -> None:
        """Attach a project once to this user's project collection."""
        if project not in self.projects:
            self.projects.append(project)

    def to_dict(self) -> dict[str, Any]:
        """Return user fields and project IDs for JSON persistence."""
        record = super().to_dict()
        record["project_ids"] = [project.id for project in self.projects]
        return record

    @classmethod
    def from_dict(cls, record: dict[str, Any]) -> User:
        """Create a user from serialized identity fields."""
        return cls(name=record["name"], email=record["email"], entity_id=int(record["id"]))

    def __str__(self) -> str:
        """Return a CLI-friendly user summary including project count."""
        return f"{super().__str__()} | projects: {len(self.projects)}"
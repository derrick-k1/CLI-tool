"""Shared person model and serialization helpers."""

from __future__ import annotations

from typing import Any, TypeVar

ModelType = TypeVar("ModelType", bound="Person")


class Person:
    """Represent a named person with a unique, monotonically assigned ID."""

    _next_id = 1

    def __init__(self, name: str, email: str, entity_id: int | None = None) -> None:
        """Initialize a person and advance the concrete class ID counter."""
        self._id = entity_id if entity_id is not None else type(self)._next_id
        type(self)._next_id = max(type(self)._next_id, self._id + 1)
        self.name = name
        self.email = email

    @property
    def id(self) -> int:
        """Return this person's stable identifier."""
        return self._id

    @property
    def name(self) -> str:
        """Return the person's display name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set a non-empty display name."""
        clean_value = value.strip()
        if not clean_value:
            raise ValueError("Name cannot be empty.")
        self._name = clean_value

    @property
    def email(self) -> str:
        """Return the person's email address."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Set a basic, non-empty email address."""
        clean_value = value.strip()
        if "@" not in clean_value or clean_value.startswith("@") or clean_value.endswith("@"):
            raise ValueError("Enter a valid email address.")
        self._email = clean_value

    def to_dict(self) -> dict[str, Any]:
        """Return the serializable fields shared by people."""
        return {"id": self.id, "name": self.name, "email": self.email}

    @classmethod
    def from_dict(cls: type[ModelType], record: dict[str, Any]) -> ModelType:
        """Build a person instance from one JSON record."""
        return cls(name=record["name"], email=record["email"], entity_id=int(record["id"]))

    @classmethod
    def collection(cls: type[ModelType], records: list[dict[str, Any]]) -> list[ModelType]:
        """Create a model collection from serialized records."""
        return [cls.from_dict(record) for record in records]

    def __str__(self) -> str:
        """Return a concise CLI-friendly person label."""
        return f"{self.name} <{self.email}> (#{self.id})"
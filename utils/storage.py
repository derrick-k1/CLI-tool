"""JSON persistence with safe handling of absent or malformed data."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)
EMPTY_DATA: dict[str, list[dict[str, Any]]] = {"users": [], "projects": [], "tasks": []}


class JsonStore:
    """Load and save the task manager's three JSON collections."""

    def __init__(self, file_path: str | Path) -> None:
        """Initialize storage at a caller-selected JSON path."""
        self.file_path = Path(file_path)

    def load(self) -> dict[str, list[dict[str, Any]]]:
        """Load validated collections or return empty collections on bad input."""
        if not self.file_path.exists():
            return {key: [] for key in EMPTY_DATA}
        try:
            raw_data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if not isinstance(raw_data, dict):
                raise ValueError("Top-level JSON value must be an object.")
            data: dict[str, list[dict[str, Any]]] = {}
            for key in EMPTY_DATA:
                value = raw_data.get(key, [])
                if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
                    raise ValueError(f"'{key}' must be a list of objects.")
                data[key] = value
            return data
        except (OSError, json.JSONDecodeError, ValueError) as error:
            LOGGER.warning("Could not load %s: %s; starting with empty data.", self.file_path, error)
            return {key: [] for key in EMPTY_DATA}

    def save(self, data: dict[str, list[dict[str, Any]]]) -> None:
        """Write collections as readable UTF-8 JSON, creating parent folders."""
        normalized = {key: data.get(key, []) for key in EMPTY_DATA}
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
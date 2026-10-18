"""Unit tests for models, relationships, and JSON persistence."""

import json
import tempfile
import unittest
from pathlib import Path

from models import Project, Task, TaskManager, User
from utils.storage import JsonStore


class ModelTests(unittest.TestCase):
    """Exercise model class methods, validation, and relationship loading."""

    def setUp(self) -> None:
        """Reset ID counters so each test has predictable fixtures."""
        User._next_id = 1
        Project._next_id = 1
        Task._next_id = 1

    def test_collection_class_methods_build_models(self) -> None:
        """Build each entity type from JSON-like records."""
        users = User.collection([{"id": 7, "name": "Alex", "email": "alex@example.com"}])
        projects = Project.collection([{
            "id": 8, "user_id": 7, "title": "CLI Tool", "description": "", "due_date": None,
        }])
        tasks = Task.collection([{
            "id": 9, "project_id": 8, "title": "Add task", "status": "todo", "assigned_to": None,
        }])

        self.assertIsInstance(users[0], User)
        self.assertIsInstance(projects[0], Project)
        self.assertIsInstance(tasks[0], Task)
        self.assertEqual((users[0].id, projects[0].id, tasks[0].id), (7, 8, 9))

    def test_properties_validate_and_normalize_values(self) -> None:
        """Reject invalid required fields and normalize task status."""
        user = User(" Alex ", "alex@example.com")
        task = Task("Ship it", 1, status="DONE")

        self.assertEqual(user.name, "Alex")
        self.assertEqual(task.status, "done")
        with self.assertRaises(ValueError):
            user.email = "not-an-email"
        with self.assertRaises(ValueError):
            task.status = "blocked"

    def test_manager_round_trip_restores_relationships(self) -> None:
        """Persist entities and restore user-project-task object links."""
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "state.json"
            manager = TaskManager(JsonStore(file_path))
            user = manager.add_user("Alex", "alex@example.com")
            project = manager.add_project(user.name, "CLI Tool", "A small CLI")
            task = manager.add_task(project.title, "Implement add-task", user.name)

            restored = TaskManager(JsonStore(file_path))

            self.assertEqual(restored.users[0].projects[0].id, project.id)
            self.assertEqual(restored.projects[0].tasks[0].id, task.id)
            self.assertEqual(restored.projects[0].tasks[0].assigned_to, "Alex")

    def test_missing_and_malformed_json_start_empty(self) -> None:
        """Return empty collections for absent or malformed data files."""
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "state.json"
            store = JsonStore(file_path)
            self.assertEqual(store.load(), {"users": [], "projects": [], "tasks": []})
            file_path.write_text("{broken", encoding="utf-8")
            self.assertEqual(store.load(), {"users": [], "projects": [], "tasks": []})
            file_path.write_text('{"users": [{}]}', encoding="utf-8")
            self.assertEqual(TaskManager(store).users, [])
            file_path.write_text(
                '{"users": [{"id": 1, "name": 42, "email": "alex@example.com"}]}',
                encoding="utf-8",
            )
            self.assertEqual(TaskManager(store).users, [])

    def test_store_round_trip_uses_json(self) -> None:
        """Write and read all supported JSON collections."""
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(Path(directory) / "nested" / "state.json")
            data = {"users": [{"id": 1}], "projects": [], "tasks": []}
            store.save(data)
            self.assertEqual(json.loads(store.file_path.read_text(encoding="utf-8")), data)
            self.assertEqual(store.load(), data)


if __name__ == "__main__":
    unittest.main()
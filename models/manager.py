"""Application operations for users, projects, and tasks."""

from __future__ import annotations

import logging
from typing import Any

from .project import Project
from .task import Task
from .user import User
from utils.storage import JsonStore

LOGGER = logging.getLogger(__name__)


class TaskManager:
    """Coordinate model relationships and persist each successful mutation."""

    def __init__(self, store: JsonStore) -> None:
        """Load records and hydrate the user-project-task object graph."""
        self.store = store
        data = store.load()
        try:
            self.users = User.collection(data["users"])
            self.projects = Project.collection(data["projects"])
            self.tasks = Task.collection(data["tasks"])
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            LOGGER.warning("Could not load model records: %s; starting with empty data.", error)
            self.users = []
            self.projects = []
            self.tasks = []
        users_by_id = {user.id: user for user in self.users}
        projects_by_id = {project.id: project for project in self.projects}
        for project in self.projects:
            owner = users_by_id.get(project.user_id)
            if owner is None:
                LOGGER.warning("Skipping project #%s with missing owner #%s.", project.id, project.user_id)
            else:
                owner.add_project(project)
        for task in self.tasks:
            project = projects_by_id.get(task.project_id)
            if project is None:
                LOGGER.warning("Skipping task #%s with missing project #%s.", task.id, task.project_id)
            else:
                project.add_task(task)

    def save(self) -> None:
        """Persist all current model collections."""
        self.store.save({
            "users": [user.to_dict() for user in self.users],
            "projects": [project.to_dict() for project in self.projects],
            "tasks": [task.to_dict() for task in self.tasks],
        })

    def add_user(self, name: str, email: str) -> User:
        """Create a user after preventing duplicate names and email addresses."""
        if any(user.name.casefold() == name.strip().casefold() for user in self.users):
            raise ValueError(f"A user named '{name}' already exists.")
        if any(user.email.casefold() == email.strip().casefold() for user in self.users):
            raise ValueError(f"A user with email '{email}' already exists.")
        user = User(name, email)
        self.users.append(user)
        self.save()
        return user

    def add_project(
        self,
        user_identifier: str,
        title: str,
        description: str = "",
        due_date: str | None = None,
    ) -> Project:
        """Create a project and attach it to its owner."""
        owner = self.find_user(user_identifier)
        if any(project.user_id == owner.id and project.title.casefold() == title.strip().casefold()
               for project in self.projects):
            raise ValueError(f"That user already has a project titled '{title}'.")
        project = Project(title, owner.id, description, due_date)
        self.projects.append(project)
        owner.add_project(project)
        self.save()
        return project

    def add_task(
        self,
        project_identifier: str,
        title: str,
        assigned_to: str | None = None,
        status: str = "todo",
    ) -> Task:
        """Create a task and attach it to its project."""
        project = self.find_project(project_identifier)
        if assigned_to:
            assigned_to = self.find_user(assigned_to).name
        if any(task.project_id == project.id and task.title.casefold() == title.strip().casefold()
               for task in self.tasks):
            raise ValueError(f"That project already has a task titled '{title}'.")
        task = Task(title, project.id, status, assigned_to)
        self.tasks.append(task)
        project.add_task(task)
        self.save()
        return task

    def find_user(self, identifier: str) -> User:
        """Find a user by numeric ID, name, or email address."""
        matches = [
            user for user in self.users
            if str(user.id) == identifier.strip()
            or user.name.casefold() == identifier.strip().casefold()
            or user.email.casefold() == identifier.strip().casefold()
        ]
        return self._one_match(matches, "user", identifier)

    def find_project(self, identifier: str) -> Project:
        """Find a project by numeric ID or exact title."""
        matches = [
            project for project in self.projects
            if str(project.id) == identifier.strip()
            or project.title.casefold() == identifier.strip().casefold()
        ]
        return self._one_match(matches, "project", identifier)

    def find_task(self, identifier: str) -> Task:
        """Find a task by numeric ID or exact title."""
        matches = [
            task for task in self.tasks
            if str(task.id) == identifier.strip()
            or task.title.casefold() == identifier.strip().casefold()
        ]
        return self._one_match(matches, "task", identifier)

    def update_user(self, identifier: str, name: str | None, email: str | None) -> User:
        """Update a user's supplied fields and persist the result."""
        user = self.find_user(identifier)
        if name:
            if any(other.id != user.id and other.name.casefold() == name.strip().casefold()
                   for other in self.users):
                raise ValueError(f"A user named '{name}' already exists.")
            user.name = name
        if email:
            if any(other.id != user.id and other.email.casefold() == email.strip().casefold()
                   for other in self.users):
                raise ValueError(f"A user with email '{email}' already exists.")
            user.email = email
        self.save()
        return user

    def update_project(
        self,
        identifier: str,
        title: str | None,
        description: str | None,
        due_date: str | None,
    ) -> Project:
        """Update a project's supplied fields and persist the result."""
        project = self.find_project(identifier)
        if title:
            project.title = title
        if description is not None:
            project.description = description
        if due_date:
            project.due_date = due_date
        self.save()
        return project

    def update_task(
        self,
        identifier: str,
        title: str | None,
        status: str | None,
        assigned_to: str | None,
    ) -> Task:
        """Update a task's supplied fields and persist the result."""
        task = self.find_task(identifier)
        if title:
            task.title = title
        if status:
            task.status = status
        if assigned_to is not None:
            task.assigned_to = self.find_user(assigned_to).name if assigned_to else None
        self.save()
        return task

    def _one_match(self, matches: list[Any], entity: str, identifier: str) -> Any:
        """Return one lookup result or raise a clear not-found/ambiguous error."""
        if not matches:
            raise ValueError(f"No {entity} found for '{identifier}'.")
        if len(matches) > 1:
            raise ValueError(f"More than one {entity} matches '{identifier}'; use its numeric ID.")
        return matches[0]
"""Argparse entry point for the task manager CLI."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

from rich.console import Console

from models.manager import TaskManager
from models.project import Project
from models.task import Task
from models.user import User
from utils.display import render_table
from utils.storage import JsonStore

DEFAULT_DATA_FILE = Path(__file__).resolve().parent / "data" / "task_manager.json"


def create_parser() -> argparse.ArgumentParser:
    """Build the command parser and all supported entity operations."""
    parser = argparse.ArgumentParser(description="Manage users, projects, and tasks.")
    parser.add_argument("--data", default=str(DEFAULT_DATA_FILE), help="JSON data file path.")
    commands = parser.add_subparsers(dest="command", required=True)

    def add_entity_commands(
        singular: str,
        plural: str,
        add_arguments: list[tuple[str, dict[str, object]]],
        update_arguments: list[tuple[str, dict[str, object]]],
    ) -> None:
        """Register the common add, list, view, and update command shape."""
        add_parser = commands.add_parser(f"add-{singular}", help=f"Add a {singular}.")
        for flag, options in add_arguments:
            add_parser.add_argument(flag, **options)
        list_parser = commands.add_parser(f"list-{plural}", help=f"List {plural}.")
        if singular in ("project", "task"):
            list_parser.add_argument(f"--{ 'user' if singular == 'project' else 'project' }")
        view_parser = commands.add_parser(f"view-{singular}", help=f"View one {singular}.")
        view_parser.add_argument(singular, help=f"{singular.title()} ID or name/title.")
        update_parser = commands.add_parser(f"update-{singular}", help=f"Update a {singular}.")
        update_parser.add_argument(singular, help=f"{singular.title()} ID or name/title.")
        for flag, options in update_arguments:
            update_parser.add_argument(flag, **options)

    add_entity_commands(
        "user", "users", [("--name", {"required": True}), ("--email", {})],
        [("--name", {}), ("--email", {})],
    )
    add_entity_commands(
        "project", "projects",
        [("--user", {"required": True}), ("--title", {"required": True}),
         ("--description", {"default": ""}), ("--due-date", {})],
        [("--title", {}), ("--description", {}), ("--due-date", {})],
    )
    add_entity_commands(
        "task", "tasks",
        [("--project", {"required": True}), ("--title", {"required": True}),
         ("--assigned-to", {}), ("--status", {"choices": Task.STATUSES, "default": "todo"})],
        [("--title", {}), ("--status", {"choices": Task.STATUSES}), ("--assigned-to", {})],
    )
    complete_parser = commands.add_parser("complete-task", help="Mark a task as done.")
    complete_parser.add_argument("task", help="Task ID or title.")
    return parser


def _user_row(user: User) -> list[str]:
    """Convert a user model to table cells."""
    return [str(user.id), user.name, user.email, str(len(user.projects))]


def _project_row(project: Project) -> list[str]:
    """Convert a project model to table cells."""
    return [str(project.id), project.title, str(project.user_id), project.due_date or "", str(len(project.tasks))]


def _task_row(task: Task) -> list[str]:
    """Convert a task model to table cells."""
    return [str(task.id), task.title, str(task.project_id), task.status, task.assigned_to or ""]


def handle_command(args: argparse.Namespace, manager: TaskManager, console: Console) -> None:
    """Execute one parsed command and render its result."""
    command = args.command
    if command == "add-user":
        email = args.email or input("Email: ")
        console.print(f"Added user: {manager.add_user(args.name, email)}")
    elif command == "list-users":
        render_table(console, "Users", ["ID", "Name", "Email", "Projects"], [_user_row(user) for user in manager.users])
    elif command == "view-user":
        console.print(manager.find_user(args.user))
    elif command == "update-user":
        console.print(f"Updated user: {manager.update_user(args.user, args.name, args.email)}")
    elif command == "add-project":
        project = manager.add_project(args.user, args.title, args.description, args.due_date)
        console.print(f"Added project: {project}")
    elif command == "list-projects":
        projects = manager.projects
        if args.user:
            owner = manager.find_user(args.user)
            projects = owner.projects
        render_table(console, "Projects", ["ID", "Title", "Owner ID", "Due date", "Tasks"], [_project_row(project) for project in projects])
    elif command == "view-project":
        console.print(manager.find_project(args.project))
    elif command == "update-project":
        project = manager.update_project(args.project, args.title, args.description, args.due_date)
        console.print(f"Updated project: {project}")
    elif command == "add-task":
        task = manager.add_task(args.project, args.title, args.assigned_to, args.status)
        console.print(f"Added task: {task}")
    elif command == "list-tasks":
        tasks = manager.tasks
        if args.project:
            project = manager.find_project(args.project)
            tasks = project.tasks
        render_table(console, "Tasks", ["ID", "Title", "Project ID", "Status", "Assigned to"], [_task_row(task) for task in tasks])
    elif command == "view-task":
        console.print(manager.find_task(args.task))
    elif command == "update-task":
        task = manager.update_task(args.task, args.title, args.status, args.assigned_to)
        console.print(f"Updated task: {task}")
    elif command == "complete-task":
        task = manager.update_task(args.task, None, "done", None)
        console.print(f"Completed task: {task}")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, load persisted state, and report user-facing errors."""
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    parser = create_parser()
    args = parser.parse_args(argv)
    manager = TaskManager(JsonStore(args.data))
    try:
        handle_command(args, manager, Console())
    except (ValueError, OSError) as error:
        Console(stderr=True).print(f"Error: {error}", style="bold red")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Tests for argparse configuration and CLI input/output behavior."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from main import create_parser, handle_command, main
from models.manager import TaskManager
from models.user import User


class CliTests(unittest.TestCase):
    """Verify command parsing, mocked interactions, and end-to-end output."""

    def test_parser_accepts_requested_command_shapes(self) -> None:
        """Accept the documented add-user/project/task command forms."""
        parser = create_parser()
        user_args = parser.parse_args(["add-user", "--name", "Alex"])
        project_args = parser.parse_args([
            "add-project", "--user", "Alex", "--title", "CLI Tool",
        ])
        task_args = parser.parse_args([
            "add-task", "--project", "CLI Tool", "--title", "Implement add-task",
        ])

        self.assertEqual(user_args.command, "add-user")
        self.assertEqual(project_args.user, "Alex")
        self.assertEqual(task_args.title, "Implement add-task")

    @patch("builtins.input", return_value="alex@example.com")
    def test_add_user_prompts_for_email_and_uses_mock_manager(self, mock_input: Mock) -> None:
        """Prompt for omitted email and pass parsed data to the manager."""
        args = create_parser().parse_args(["add-user", "--name", "Alex"])
        manager = Mock(spec=TaskManager)
        manager.add_user.return_value = User("Alex", "alex@example.com")
        console = Mock()

        handle_command(args, manager, console)

        mock_input.assert_called_once_with("Email: ")
        manager.add_user.assert_called_once_with("Alex", "alex@example.com")
        console.print.assert_called_once()

    @patch("main.render_table")
    def test_list_users_renders_mock_data(self, mock_render: Mock) -> None:
        """Render the current user collection through the shared table helper."""
        user = User("Alex", "alex@example.com")
        args = create_parser().parse_args(["list-users"])
        manager = Mock(spec=TaskManager)
        manager.users = [user]
        console = Mock()

        handle_command(args, manager, console)

        self.assertIs(mock_render.call_args.args[0], console)
        self.assertEqual(mock_render.call_args.args[1], "Users")
        self.assertEqual(mock_render.call_args.args[3], [[str(user.id), "Alex", "alex@example.com", "0"]])

    def test_cli_persists_user_and_prints_confirmation(self) -> None:
        """Run a command with a temporary JSON file and captured terminal output."""
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "state.json"
            output = io.StringIO()
            with redirect_stdout(output):
                result = main([
                    "--data", str(file_path), "add-user", "--name", "Alex",
                    "--email", "alex@example.com",
                ])

            self.assertEqual(result, 0)
            self.assertIn("Added user: Alex <alex@example.com>", output.getvalue())
            saved_data = json.loads(file_path.read_text(encoding="utf-8"))
            self.assertEqual(saved_data["users"][0]["email"], "alex@example.com")


if __name__ == "__main__":
    unittest.main()
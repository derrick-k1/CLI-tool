# Task Manager CLI

A small Python command-line app for admins to manage users, projects, and tasks. Each user can own multiple projects, and each project can contain multiple tasks. Data is stored locally in JSON.

## Setup

Requires Python 3.10 or newer.

Clone the repository and open a terminal in the project directory:

```powershell
git clone https://github.com/derrick-k1/CLI-tool.git
cd CLI-tool
```

Create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Example data

The repository includes [data/sample.json](data/sample.json) with sample users, projects, and tasks. Inspect it with:

```powershell
python main.py --data data/sample.json list-users
python main.py --data data/sample.json list-projects
python main.py --data data/sample.json list-tasks
```

The default `data/task_manager.json` file is created automatically when you add or update records. Runtime JSON files are ignored by Git so your local data is not committed.

## Commands

Run commands from this project directory. The default data file is `data/task_manager.json`; pass `--data PATH` before the subcommand to use another file.

```powershell
python main.py add-user --name "Alex" --email "alex@example.com"
python main.py add-project --user "Alex" --title "CLI Tool" --description "A small project"
python main.py add-task --project "CLI Tool" --title "Implement add-task" --assigned-to "Alex"
python main.py list-users
python main.py list-projects --user "Alex"
python main.py list-tasks --project "CLI Tool"
python main.py view-project "CLI Tool"
python main.py update-task "Implement add-task" --status in_progress
python main.py complete-task "Implement add-task"
```

`add-user --name "Alex"` prompts for an email when `--email` is omitted. Entity lookups accept an ID or exact name/title; use IDs when titles are ambiguous. Task statuses are `todo`, `in_progress`, and `done`.

## Features

- `Person` and `User`, `Project`, and `Task` models with validated properties, class-level IDs, collection class methods, and readable string output.
- One-to-many user/project and project/task relationships restored when JSON data loads.
- Add, list, view, and update commands for all entities, plus `complete-task`.
- Rich tables for list output and warning logs for malformed data files.
- Unit tests for model methods, JSON behavior, argument parsing, mocked CLI input/output, and persistence.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Known Issues

- This is a local single-user data store; it has no authentication, concurrent-write protection, or database migrations.
- `add-user` requires an email, prompting interactively if one is not provided.
- Due dates must use `YYYY-MM-DD`; task status values are intentionally limited to the three documented options.
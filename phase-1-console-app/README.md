# Phase 1: Console Todo Application

This is the first phase of the console todo application. It provides basic CRUD functionality for managing tasks in memory.

## Features

- Add new tasks with title and optional description
- View all tasks with completion status
- Update existing tasks
- Delete tasks
- Mark tasks as complete/incomplete
- Menu-driven interface

## Requirements

- Python 3.8 or higher

## How to Run

1. Navigate to this directory
2. Run the application:
   ```bash
   python run.py
   ```

## Project Structure

```
src/
├── models/
│   └── task.py          # Task data model
├── services/
│   └── task_service.py  # Task management service
└── cli/
    └── main.py          # Command line interface
```

## Usage

The application provides a menu-driven interface:

1. **Add Task**: Create a new task with title and optional description
2. **View Tasks**: See all tasks with their completion status
3. **Update Task**: Modify an existing task's title or description
4. **Delete Task**: Remove a task by ID
5. **Complete Task**: Toggle a task's completion status
6. **Exit**: Quit the application

## Architecture

- **Task Model**: Represents a single task with ID, title, description, and completion status
- **Task Service**: Handles all business logic for task management in memory
- **CLI Interface**: Provides the user interface for interacting with the application
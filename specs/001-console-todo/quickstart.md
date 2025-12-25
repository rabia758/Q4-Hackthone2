# Quickstart: Console Todo Application

## Running the Application

1. Ensure Python 3.8+ is installed on your system
2. Navigate to the project directory
3. Run the application:
   ```bash
   python src/cli/main.py
   ```

## Initial Setup

The application starts with an empty task list. No configuration is required.

## Basic Usage

1. **Add a Task**: Select option 1, enter the task title and description
2. **View Tasks**: Select option 2 to see all tasks with their status
3. **Update Task**: Select option 3, enter task ID and new details
4. **Delete Task**: Select option 4, enter task ID to remove
5. **Complete Task**: Select option 5, enter task ID to toggle completion
6. **Exit**: Select option 6 to quit the application

## Example Workflow

```
Welcome to the Todo Application!
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Complete Task
6. Exit
Choose an option: 1
Enter task title: Buy groceries
Enter task description (optional): Get milk, bread, and eggs
Task added successfully with ID: 1

Choose an option: 2
ID: 1 | Title: Buy groceries | Completed: False | Description: Get milk, bread, and eggs
```
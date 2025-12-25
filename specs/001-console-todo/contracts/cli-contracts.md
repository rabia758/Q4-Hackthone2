# API Contracts: Console Todo Application

Since this is a console application, we define the functional contracts as command-line interface contracts:

## CLI Commands

### 1. Add Task
- **Input**: `add_task(title: str, description: str = None)`
- **Output**: `task_id: int`
- **Side Effect**: Creates new task in memory
- **Validation**: Title must not be empty
- **Error Handling**: Raises ValueError if title is empty

### 2. View Tasks
- **Input**: `view_tasks()`
- **Output**: `List[Task]`
- **Side Effect**: None
- **Validation**: None
- **Error Handling**: None

### 3. Update Task
- **Input**: `update_task(task_id: int, title: str = None, description: str = None)`
- **Output**: `bool` (success/failure)
- **Side Effect**: Modifies existing task
- **Validation**: Task must exist
- **Error Handling**: Returns False if task doesn't exist

### 4. Delete Task
- **Input**: `delete_task(task_id: int)`
- **Output**: `bool` (success/failure)
- **Side Effect**: Removes task from memory
- **Validation**: Task must exist
- **Error Handling**: Returns False if task doesn't exist

### 5. Complete Task
- **Input**: `toggle_completion(task_id: int)`
- **Output**: `bool` (success/failure)
- **Side Effect**: Toggles completion status
- **Validation**: Task must exist
- **Error Handling**: Returns False if task doesn't exist

## Data Contracts

### Task
```python
{
    "id": int,           # Required, positive integer
    "title": str,        # Required, non-empty string
    "description": str,  # Optional, can be None or string
    "completed": bool    # Required, boolean value
}
```
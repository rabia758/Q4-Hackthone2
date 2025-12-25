# Data Model: Console Todo Application

## Task Entity

### Fields
- **id**: integer (auto-incremented)
  - Unique identifier for each task
  - Primary key for the task
  - Auto-incremented when new task is created

- **title**: string (required)
  - Required field for task description
  - Cannot be empty or null
  - Maximum length: 255 characters

- **description**: string (optional)
  - Optional field for detailed task information
  - Can be empty or null
  - Maximum length: 1000 characters

- **completed**: boolean (default: false)
  - Indicates completion status
  - Default value is false (incomplete)
  - Can be toggled between true and false

### Validation Rules
- Title must not be empty or contain only whitespace
- ID must be unique within the application session
- ID must be a positive integer
- Completed field must be a boolean value

### State Transitions
- New task: `completed = false` (default)
- Task completion: `completed = false` → `completed = true`
- Task uncompletion: `completed = true` → `completed = false`

### Example
```python
task = {
    "id": 1,
    "title": "Complete project",
    "description": "Finish the todo application project",
    "completed": False
}
```
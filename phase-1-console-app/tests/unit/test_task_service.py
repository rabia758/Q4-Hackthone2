"""
Unit tests for the TaskService
"""
from src.services.task_service import TaskService


def test_add_task():
    """Test adding a task"""
    service = TaskService()
    task = service.add_task("Test Task", "Test Description")

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert len(service.get_all_tasks()) == 1


def test_add_task_without_description():
    """Test adding a task without description"""
    service = TaskService()
    task = service.add_task("Test Task")

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description is None
    assert task.completed is False


def test_add_task_empty_title():
    """Test that adding a task with empty title raises error"""
    service = TaskService()
    try:
        service.add_task("")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Task title cannot be empty"


def test_get_all_tasks():
    """Test getting all tasks"""
    service = TaskService()
    service.add_task("Task 1")
    service.add_task("Task 2")

    tasks = service.get_all_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"


def test_update_task():
    """Test updating a task"""
    service = TaskService()
    task = service.add_task("Original Title", "Original Description")

    result = service.update_task(task.id, "Updated Title", "Updated Description")

    assert result is True
    updated_task = service.get_all_tasks()[0]
    assert updated_task.title == "Updated Title"
    assert updated_task.description == "Updated Description"


def test_update_task_not_found():
    """Test updating a non-existent task"""
    service = TaskService()

    result = service.update_task(999, "Updated Title")

    assert result is False


def test_delete_task():
    """Test deleting a task"""
    service = TaskService()
    task = service.add_task("Test Task")

    result = service.delete_task(task.id)

    assert result is True
    assert len(service.get_all_tasks()) == 0


def test_delete_task_not_found():
    """Test deleting a non-existent task"""
    service = TaskService()

    result = service.delete_task(999)

    assert result is False


def test_toggle_completion():
    """Test toggling task completion"""
    service = TaskService()
    task = service.add_task("Test Task")

    # Initially should be False
    assert task.completed is False

    # Toggle to True
    result = service.toggle_completion(task.id)
    assert result is True
    toggled_task = service.get_all_tasks()[0]
    assert toggled_task.completed is True

    # Toggle back to False
    result = service.toggle_completion(task.id)
    assert result is True
    toggled_task = service.get_all_tasks()[0]
    assert toggled_task.completed is False


def test_toggle_completion_not_found():
    """Test toggling completion of a non-existent task"""
    service = TaskService()

    result = service.toggle_completion(999)

    assert result is False
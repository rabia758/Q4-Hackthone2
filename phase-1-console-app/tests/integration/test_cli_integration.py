"""
Integration tests for the CLI functionality
"""
from src.services.task_service import TaskService


def test_full_task_lifecycle():
    """Test the full lifecycle of a task through the service"""
    service = TaskService()

    # Add a task
    task = service.add_task("Integration Test Task", "Test description for integration")
    assert task.id == 1
    assert task.title == "Integration Test Task"
    assert task.description == "Test description for integration"
    assert task.completed is False

    # Verify it's in the list
    tasks = service.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == 1

    # Update the task
    result = service.update_task(task.id, "Updated Integration Test Task", "Updated description")
    assert result is True

    # Verify the update
    updated_task = service.get_all_tasks()[0]
    assert updated_task.title == "Updated Integration Test Task"
    assert updated_task.description == "Updated description"

    # Toggle completion
    result = service.toggle_completion(task.id)
    assert result is True
    completed_task = service.get_all_tasks()[0]
    assert completed_task.completed is True

    # Toggle completion back
    result = service.toggle_completion(task.id)
    assert result is True
    incomplete_task = service.get_all_tasks()[0]
    assert incomplete_task.completed is False

    # Delete the task
    result = service.delete_task(task.id)
    assert result is True

    # Verify it's gone
    tasks = service.get_all_tasks()
    assert len(tasks) == 0


def test_multiple_tasks():
    """Test working with multiple tasks"""
    service = TaskService()

    # Add multiple tasks
    task1 = service.add_task("Task 1", "First task")
    task2 = service.add_task("Task 2", "Second task")
    task3 = service.add_task("Task 3", "Third task")

    # Verify all tasks exist
    tasks = service.get_all_tasks()
    assert len(tasks) == 3
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"
    assert tasks[2].title == "Task 3"

    # Verify IDs are sequential
    assert tasks[0].id == 1
    assert tasks[1].id == 2
    assert tasks[2].id == 3

    # Update middle task
    service.update_task(task2.id, "Updated Task 2")
    updated_tasks = service.get_all_tasks()
    assert updated_tasks[1].title == "Updated Task 2"

    # Toggle completion of first task
    service.toggle_completion(task1.id)
    updated_tasks = service.get_all_tasks()
    assert updated_tasks[0].completed is True
    assert updated_tasks[1].completed is False
    assert updated_tasks[2].completed is False

    # Delete second task
    service.delete_task(task2.id)
    remaining_tasks = service.get_all_tasks()
    assert len(remaining_tasks) == 2
    assert remaining_tasks[0].id == 1  # Task 1
    assert remaining_tasks[1].id == 3  # Task 3
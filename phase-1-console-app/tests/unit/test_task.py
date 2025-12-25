"""
Unit tests for the Task model
"""
import pytest
from src.models.task import Task


def test_task_creation():
    """Test creating a task with valid data"""
    task = Task(id=1, title="Test Task", description="Test Description", completed=False)
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False


def test_task_creation_defaults():
    """Test creating a task with default values"""
    task = Task(id=1, title="Test Task")
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description is None
    assert task.completed is False


def test_task_title_validation():
    """Test that task creation fails with empty title"""
    try:
        Task(id=1, title="")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Task title cannot be empty"

    try:
        Task(id=1, title="   ")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Task title cannot be empty"
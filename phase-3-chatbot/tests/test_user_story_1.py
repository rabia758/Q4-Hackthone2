"""
Test cases for User Story 1: Natural Language Todo Creation
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.backend.lib.ai_utils import detect_intent


def test_create_todo_with_add_command():
    """Test creating a todo with 'add a todo to' command"""
    message = "Add a todo to buy groceries"
    intent, entities = detect_intent(message)

    assert intent == "CREATE"
    assert entities["title"] == "buy groceries"


def test_create_todo_with_create_task_command():
    """Test creating a todo with 'create a task to' command"""
    message = "Create a task to call John tomorrow"
    intent, entities = detect_intent(message)

    assert intent == "CREATE"
    assert entities["title"] == "call John tomorrow"


def test_create_todo_with_create_todo_command():
    """Test creating a todo with 'create a todo to' command"""
    message = "Create a todo to finish project"
    intent, entities = detect_intent(message)

    assert intent == "CREATE"
    assert entities["title"] == "finish project"


def test_create_todo_with_make_todo_command():
    """Test creating a todo with 'make a todo to' command"""
    message = "Make a todo to schedule meeting"
    intent, entities = detect_intent(message)

    assert intent == "CREATE"
    assert entities["title"] == "schedule meeting"


def test_create_todo_with_add_to_my_todos_command():
    """Test creating a todo with 'add X to my todos' command"""
    message = "Add review documents to my todos"
    intent, entities = detect_intent(message)

    assert intent == "CREATE"
    assert entities["title"] == "review documents"


def test_unknown_intent():
    """Test that unrecognized commands return UNKNOWN intent"""
    message = "What is the weather like today?"
    intent, entities = detect_intent(message)

    assert intent == "UNKNOWN"


if __name__ == "__main__":
    pytest.main([__file__])
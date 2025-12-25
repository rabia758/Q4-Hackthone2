"""
Task model for the console todo application
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """
    Represents a task in the todo application
    """
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False

    def __post_init__(self):
        """Validate the task after initialization"""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
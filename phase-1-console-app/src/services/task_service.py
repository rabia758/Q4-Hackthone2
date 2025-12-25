"""
Task service for the console todo application
"""
from typing import List, Optional
from ..models.task import Task


class TaskService:
    """
    Service class to manage tasks in memory
    """
    def __init__(self):
        self.tasks: List[Task] = []
        self._next_id = 1

    def add_task(self, title: str, description: Optional[str] = None) -> Task:
        """
        Add a new task to the list
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        task = Task(
            id=self._next_id,
            title=title.strip(),
            description=description,
            completed=False
        )
        self.tasks.append(task)
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks
        """
        return self.tasks.copy()

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        """
        Update a task by ID
        """
        task = self._find_task_by_id(task_id)
        if task:
            if title is not None:
                if not title.strip():
                    raise ValueError("Task title cannot be empty")
                task.title = title.strip()
            if description is not None:
                task.description = description
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID
        """
        task = self._find_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

    def toggle_completion(self, task_id: int) -> bool:
        """
        Toggle the completion status of a task by ID
        """
        task = self._find_task_by_id(task_id)
        if task:
            task.completed = not task.completed
            return True
        return False

    def _find_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Find a task by its ID
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
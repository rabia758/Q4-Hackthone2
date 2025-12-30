"""
Todo service for handling todo operations with AI integration
"""
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from sqlmodel import Session, select
from models import Todo, TodoCreate, TodoUpdate


class TodoService:
    """
    Service class for handling todo operations
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_todo(self, todo_create: TodoCreate) -> Todo:
        """
        Create a new todo
        """
        todo = Todo(
            title=todo_create.title,
            user_id=todo_create.user_id,
            completed=False,
            created_at=datetime.now()
        )
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def get_todos(self, user_id: str, completed: Optional[bool] = None) -> List[Todo]:
        """
        Get todos for a user, optionally filtered by completion status
        """
        query = select(Todo).where(Todo.user_id == user_id)

        if completed is not None:
            query = query.where(Todo.completed == completed)

        query = query.order_by(Todo.created_at.desc())

        return self.db.exec(query).all()

    def get_todo_by_title(self, user_id: str, title: str) -> Optional[Todo]:
        """
        Get a todo by user_id and title (for fuzzy matching)
        """
        query = select(Todo).where(
            Todo.user_id == user_id,
            Todo.title.ilike(f"%{title}%")  # Case-insensitive partial match
        )
        return self.db.exec(query).first()

    def update_todo(self, todo_id: uuid.UUID, todo_update: TodoUpdate) -> Optional[Todo]:
        """
        Update a todo
        """
        todo = self.db.get(Todo, todo_id)
        if not todo:
            return None

        # Update fields that were provided
        for field, value in todo_update.dict(exclude_unset=True).items():
            setattr(todo, field, value)

        todo.updated_at = datetime.now()
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def update_todo_by_title(self, user_id: str, title: str, todo_update: TodoUpdate) -> Optional[Todo]:
        """
        Update a todo by user_id and title (for fuzzy matching)
        """
        todo = self.get_todo_by_title(user_id, title)
        if not todo:
            return None

        # Update fields that were provided
        for field, value in todo_update.dict(exclude_unset=True).items():
            setattr(todo, field, value)

        todo.updated_at = datetime.now()
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete_todo(self, todo_id: uuid.UUID) -> bool:
        """
        Delete a todo
        """
        todo = self.db.get(Todo, todo_id)
        if not todo:
            return False

        self.db.delete(todo)
        self.db.commit()
        return True

    def delete_todo_by_title(self, user_id: str, title: str) -> bool:
        """
        Delete a todo by user_id and title (for fuzzy matching)
        """
        todo = self.get_todo_by_title(user_id, title)
        if not todo:
            return False

        self.db.delete(todo)
        self.db.commit()
        return True
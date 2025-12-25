"""
Main CLI interface for the console todo application
"""
import sys
from typing import Optional
from ..services.task_service import TaskService


class TodoCLI:
    """
    Command Line Interface for the Todo application
    """
    def __init__(self):
        self.service = TaskService()

    def run(self):
        """
        Run the main application loop
        """
        print("Welcome to the Todo Application!")
        while True:
            self._display_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                self._add_task()
            elif choice == "2":
                self._view_tasks()
            elif choice == "3":
                self._update_task()
            elif choice == "4":
                self._delete_task()
            elif choice == "5":
                self._complete_task()
            elif choice == "6":
                print("Goodbye!")
                sys.exit(0)
            else:
                print("Invalid option. Please choose a number from 1-6.")

    def _display_menu(self):
        """
        Display the main menu
        """
        print("\n" + "="*40)
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Complete Task")
        print("6. Exit")
        print("="*40)

    def _add_task(self):
        """
        Add a new task
        """
        try:
            title = input("Enter task title: ").strip()
            if not title:
                print("Error: Task title cannot be empty")
                return

            description = input("Enter task description (optional): ").strip()
            if not description:  # If description is empty, set to None
                description = None

            task = self.service.add_task(title, description)
            print(f"Task added successfully with ID: {task.id}")
        except ValueError as e:
            print(f"Error: {e}")

    def _view_tasks(self):
        """
        View all tasks
        """
        tasks = self.service.get_all_tasks()
        if not tasks:
            print("No tasks found.")
            return

        print("\nYour Tasks:")
        for task in tasks:
            status = "✓" if task.completed else "○"
            print(f"ID: {task.id} | {status} | Title: {task.title}")
            if task.description:
                print(f"  Description: {task.description}")
            print("-" * 40)

    def _update_task(self):
        """
        Update a task
        """
        try:
            task_id_str = input("Enter task ID to update: ").strip()
            if not task_id_str.isdigit():
                print("Error: Task ID must be a number")
                return

            task_id = int(task_id_str)
            task = self._find_task_by_id(task_id)
            if not task:
                print(f"Error: Task with ID {task_id} not found")
                return

            title = input(f"Enter new title (current: '{task.title}'): ").strip()
            if not title:  # If empty, keep the current title
                title = task.title

            description = input(f"Enter new description (current: '{task.description or ''}'): ").strip()
            if description == '':  # If empty string, keep current or set to None if was None
                description = task.description
            elif not description:  # If None was entered (though input returns string)
                description = None

            if self.service.update_task(task_id, title, description):
                print("Task updated successfully")
            else:
                print("Error updating task")
        except ValueError as e:
            print(f"Error: {e}")

    def _delete_task(self):
        """
        Delete a task
        """
        task_id_str = input("Enter task ID to delete: ").strip()
        if not task_id_str.isdigit():
            print("Error: Task ID must be a number")
            return

        task_id = int(task_id_str)
        if self.service.delete_task(task_id):
            print("Task deleted successfully")
        else:
            print(f"Error: Task with ID {task_id} not found")

    def _complete_task(self):
        """
        Toggle task completion status
        """
        task_id_str = input("Enter task ID to toggle completion: ").strip()
        if not task_id_str.isdigit():
            print("Error: Task ID must be a number")
            return

        task_id = int(task_id_str)
        if self.service.toggle_completion(task_id):
            task = self._find_task_by_id(task_id)
            status = "completed" if task.completed else "incomplete"
            print(f"Task marked as {status}")
        else:
            print(f"Error: Task with ID {task_id} not found")

    def _find_task_by_id(self, task_id: int):
        """
        Find a task by its ID (helper method)
        """
        for task in self.service.get_all_tasks():
            if task.id == task_id:
                return task
        return None


def main():
    """
    Main function to start the application
    """
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()
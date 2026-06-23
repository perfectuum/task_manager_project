"""Business logic for task management."""

from datetime import datetime
from typing import Any

from task_manager.models import DATE_FORMAT, Task, TaskValidationError, normalize_due_date, normalize_priority, normalize_status
from task_manager.storage import CsvTaskStorage


class TaskNotFoundError(LookupError):
    """Raised when a task with the requested id does not exist."""


class TaskManager:
    """Application service that provides CRUD, search and task-specific operations."""

    def __init__(self, storage: CsvTaskStorage) -> None:
        self.storage = storage

    def _load(self) -> list[Task]:
        return self.storage.read_tasks()

    def _save(self, tasks: list[Task]) -> None:
        self.storage.write_tasks(tasks)

    @staticmethod
    def _next_id(tasks: list[Task]) -> int:
        if not tasks:
            return 1
        return max(task.id for task in tasks) + 1

    def create_task(self, title: str, description: str, priority: str, due_date: str) -> Task:
        tasks = self._load()
        task = Task(
            id=self._next_id(tasks),
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            status="todo",
        )
        tasks.append(task)
        self._save(tasks)
        return task

    def list_tasks(self, status: str | None = None, priority: str | None = None) -> list[Task]:
        tasks = self._load()
        if status is not None:
            normalized_status = normalize_status(status)
            tasks = [task for task in tasks if task.status == normalized_status]
        if priority is not None:
            normalized_priority = normalize_priority(priority)
            tasks = [task for task in tasks if task.priority == normalized_priority]
        return sorted(tasks, key=lambda task: (task.due_date, task.id))

    def get_task(self, task_id: int) -> Task:
        for task in self._load():
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"Task with id {task_id} was not found")

    def update_task(self, task_id: int, **changes: Any) -> Task:
        tasks = self._load()
        updated_task: Task | None = None
        result: list[Task] = []
        allowed_fields = {"title", "description", "priority", "due_date", "status"}
        unknown_fields = set(changes) - allowed_fields
        if unknown_fields:
            raise TaskValidationError(f"Unknown task fields: {', '.join(sorted(unknown_fields))}")

        for task in tasks:
            if task.id != task_id:
                result.append(task)
                continue
            data = task.to_dict()
            data.update({key: str(value) for key, value in changes.items() if value is not None})
            updated_task = Task.from_dict(data)
            result.append(updated_task)

        if updated_task is None:
            raise TaskNotFoundError(f"Task with id {task_id} was not found")
        self._save(result)
        return updated_task

    def delete_task(self, task_id: int) -> None:
        tasks = self._load()
        result = [task for task in tasks if task.id != task_id]
        if len(result) == len(tasks):
            raise TaskNotFoundError(f"Task with id {task_id} was not found")
        self._save(result)

    def mark_done(self, task_id: int) -> Task:
        return self.update_task(task_id, status="done")

    def reopen_task(self, task_id: int) -> Task:
        return self.update_task(task_id, status="todo")

    def search_tasks(self, query: str) -> list[Task]:
        normalized_query = (query or "").strip().lower()
        if not normalized_query:
            return []
        tasks = self._load()
        found = [
            task
            for task in tasks
            if normalized_query in task.title.lower() or normalized_query in task.description.lower()
        ]
        return sorted(found, key=lambda task: (task.due_date, task.id))

    def list_overdue(self, reference_date: str) -> list[Task]:
        normalized_reference_date = normalize_due_date(reference_date)
        reference = datetime.strptime(normalized_reference_date, DATE_FORMAT).date()
        overdue: list[Task] = []
        for task in self._load():
            task_date = datetime.strptime(task.due_date, DATE_FORMAT).date()
            if task.status == "todo" and task_date < reference:
                overdue.append(task)
        return sorted(overdue, key=lambda task: (task.due_date, task.id))

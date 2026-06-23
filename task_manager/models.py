"""Domain model and validation for tasks."""

from dataclasses import dataclass
from datetime import datetime

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"todo", "done"}
DATE_FORMAT = "%Y-%m-%d"


class TaskValidationError(ValueError):
    """Raised when task data is invalid."""


def normalize_priority(priority: str) -> str:
    value = (priority or "").strip().lower()
    if value not in VALID_PRIORITIES:
        raise TaskValidationError("Priority must be one of: low, medium, high")
    return value


def normalize_status(status: str) -> str:
    value = (status or "").strip().lower()
    if value not in VALID_STATUSES:
        raise TaskValidationError("Status must be one of: todo, done")
    return value


def normalize_due_date(due_date: str) -> str:
    value = (due_date or "").strip()
    if not value:
        raise TaskValidationError("Due date is required")
    try:
        parsed = datetime.strptime(value, DATE_FORMAT).date()
    except ValueError as exc:
        raise TaskValidationError("Due date must have YYYY-MM-DD format") from exc
    return parsed.isoformat()


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    description: str
    priority: str
    due_date: str
    status: str = "todo"

    def __post_init__(self) -> None:
        if not isinstance(self.id, int) or self.id <= 0:
            raise TaskValidationError("Task id must be a positive integer")
        normalized_title = self.title.strip()
        if not normalized_title:
            raise TaskValidationError("Title is required")
        object.__setattr__(self, "title", normalized_title)
        object.__setattr__(self, "description", (self.description or "").strip())
        object.__setattr__(self, "priority", normalize_priority(self.priority))
        object.__setattr__(self, "due_date", normalize_due_date(self.due_date))
        object.__setattr__(self, "status", normalize_status(self.status))

    def to_dict(self) -> dict[str, str]:
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, row: dict[str, str]) -> "Task":
        try:
            task_id = int(row.get("id", ""))
        except ValueError as exc:
            raise TaskValidationError("Task id must be a number") from exc
        return cls(
            id=task_id,
            title=row.get("title", ""),
            description=row.get("description", ""),
            priority=row.get("priority", "medium"),
            due_date=row.get("due_date", ""),
            status=row.get("status", "todo"),
        )

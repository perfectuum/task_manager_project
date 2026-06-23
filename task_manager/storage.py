"""CSV storage layer for tasks."""

import csv
from pathlib import Path

from task_manager.models import Task

FIELDNAMES = ["id", "title", "description", "priority", "due_date", "status"]


class CsvTaskStorage:
    """Stores tasks in a CSV file using only Python standard library."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def read_tasks(self) -> list[Task]:
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            return []
        with self.file_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return [Task.from_dict(row) for row in reader]

    def write_tasks(self, tasks: list[Task]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            for task in tasks:
                writer.writerow(task.to_dict())

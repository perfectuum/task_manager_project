from task_manager.models import Task
from task_manager.storage import CsvTaskStorage


def test_read_missing_file_returns_empty_list(tmp_path):
    storage = CsvTaskStorage(tmp_path / "missing.csv")

    assert storage.read_tasks() == []


def test_write_and_read_tasks(tmp_path):
    storage = CsvTaskStorage(tmp_path / "tasks.csv")
    tasks = [
        Task(1, "Задача 1", "Описание", "high", "2026-06-25", "todo"),
        Task(2, "Задача 2", "", "low", "2026-06-26", "done"),
    ]

    storage.write_tasks(tasks)

    assert storage.read_tasks() == tasks

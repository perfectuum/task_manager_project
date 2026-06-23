import pytest

from task_manager.service import TaskManager, TaskNotFoundError
from task_manager.storage import CsvTaskStorage


@pytest.fixture
def manager(tmp_path):
    return TaskManager(CsvTaskStorage(tmp_path / "tasks.csv"))


def test_create_and_get_task(manager):
    created = manager.create_task("Сдать практическую", "Загрузить на GitHub", "high", "2026-06-25")

    found = manager.get_task(created.id)

    assert found.title == "Сдать практическую"
    assert found.description == "Загрузить на GitHub"
    assert found.priority == "high"
    assert found.status == "todo"


def test_update_task(manager):
    task = manager.create_task("Черновик", "", "low", "2026-06-24")

    updated = manager.update_task(task.id, title="Финальная версия", priority="medium")

    assert updated.title == "Финальная версия"
    assert updated.priority == "medium"
    assert manager.get_task(task.id).title == "Финальная версия"


def test_delete_task(manager):
    task = manager.create_task("Удалить", "", "low", "2026-06-24")

    manager.delete_task(task.id)

    with pytest.raises(TaskNotFoundError):
        manager.get_task(task.id)


def test_missing_task_operations_raise_error(manager):
    with pytest.raises(TaskNotFoundError):
        manager.get_task(999)
    with pytest.raises(TaskNotFoundError):
        manager.update_task(999, title="Нет")
    with pytest.raises(TaskNotFoundError):
        manager.delete_task(999)


def test_mark_done_and_reopen(manager):
    task = manager.create_task("Проверить тесты", "", "medium", "2026-06-25")

    done = manager.mark_done(task.id)
    reopened = manager.reopen_task(task.id)

    assert done.status == "done"
    assert reopened.status == "todo"

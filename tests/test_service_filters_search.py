import pytest

from task_manager.models import TaskValidationError
from task_manager.service import TaskManager
from task_manager.storage import CsvTaskStorage


@pytest.fixture
def manager(tmp_path):
    manager = TaskManager(CsvTaskStorage(tmp_path / "tasks.csv"))
    manager.create_task("Учёба", "написать тесты", "high", "2026-06-25")
    second = manager.create_task("Дом", "купить хлеб", "low", "2026-06-24")
    manager.mark_done(second.id)
    manager.create_task("Проект", "оформить README", "medium", "2026-06-26")
    return manager


def test_filter_by_status(manager):
    done_tasks = manager.list_tasks(status="done")

    assert len(done_tasks) == 1
    assert done_tasks[0].title == "Дом"


def test_filter_by_priority(manager):
    high_tasks = manager.list_tasks(priority="HIGH")

    assert len(high_tasks) == 1
    assert high_tasks[0].title == "Учёба"


def test_search_by_title_and_description(manager):
    by_title = manager.search_tasks("про")
    by_description = manager.search_tasks("тесты")

    assert [task.title for task in by_title] == ["Проект"]
    assert [task.title for task in by_description] == ["Учёба"]


def test_empty_search_returns_empty_list(manager):
    assert manager.search_tasks("   ") == []


def test_invalid_filter_value_raises_error(manager):
    with pytest.raises(TaskValidationError):
        manager.list_tasks(priority="critical")

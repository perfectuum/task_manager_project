from task_manager.service import TaskManager
from task_manager.storage import CsvTaskStorage


def test_new_task_id_uses_max_existing_id_after_delete(tmp_path):
    manager = TaskManager(CsvTaskStorage(tmp_path / "tasks.csv"))
    first = manager.create_task("Первая", "", "low", "2026-06-24")
    second = manager.create_task("Вторая", "", "low", "2026-06-25")
    manager.delete_task(first.id)

    third = manager.create_task("Третья", "", "low", "2026-06-26")

    assert second.id == 2
    assert third.id == 3


def test_list_overdue_returns_only_open_tasks_before_reference_date(tmp_path):
    manager = TaskManager(CsvTaskStorage(tmp_path / "tasks.csv"))
    overdue = manager.create_task("Просроченная", "", "high", "2026-06-20")
    done_overdue = manager.create_task("Готовая", "", "high", "2026-06-19")
    manager.mark_done(done_overdue.id)
    manager.create_task("Будущая", "", "medium", "2026-06-30")

    result = manager.list_overdue("2026-06-23")

    assert result == [overdue]


def test_priority_can_be_entered_in_any_case(tmp_path):
    manager = TaskManager(CsvTaskStorage(tmp_path / "tasks.csv"))

    task = manager.create_task("Регистры", "", "HiGh", "2026-06-25")

    assert task.priority == "high"

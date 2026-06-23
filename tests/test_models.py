import pytest

from task_manager.models import Task, TaskValidationError


def test_task_normalizes_fields():
    task = Task(
        id=1,
        title="  Купить продукты  ",
        description="  молоко  ",
        priority="HIGH",
        due_date="2026-06-25",
        status="TODO",
    )

    assert task.title == "Купить продукты"
    assert task.description == "молоко"
    assert task.priority == "high"
    assert task.status == "todo"


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", ""),
        ("priority", "urgent"),
        ("due_date", "25.06.2026"),
        ("status", "active"),
    ],
)
def test_task_rejects_invalid_values(field, value):
    data = {
        "id": 1,
        "title": "Задача",
        "description": "Описание",
        "priority": "medium",
        "due_date": "2026-06-25",
        "status": "todo",
    }
    data[field] = value

    with pytest.raises(TaskValidationError):
        Task(**data)


def test_task_rejects_invalid_id():
    with pytest.raises(TaskValidationError):
        Task(0, "Задача", "", "medium", "2026-06-25", "todo")

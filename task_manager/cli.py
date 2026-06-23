"""Console interface for the task manager."""

from pathlib import Path

from task_manager import __version__
from task_manager.models import TaskValidationError
from task_manager.service import TaskManager, TaskNotFoundError
from task_manager.storage import CsvTaskStorage


def _print_task(task) -> None:
    print(
        f"#{task.id} | {task.title} | {task.priority} | {task.due_date} | {task.status}"
        + (f" | {task.description}" if task.description else "")
    )


def _read_task_id(prompt: str = "ID задачи: ") -> int:
    raw_value = input(prompt).strip()
    if not raw_value.isdigit():
        raise TaskValidationError("ID должен быть положительным числом")
    return int(raw_value)


def run_cli(data_path: str | Path = "tasks.csv") -> None:
    manager = TaskManager(CsvTaskStorage(data_path))
    menu = """
Менеджер задач v{version}
1. Добавить задачу
2. Показать все задачи
3. Найти задачу
4. Фильтр по статусу
5. Фильтр по приоритету
6. Изменить задачу
7. Отметить выполненной
8. Удалить задачу
9. Показать просроченные
0. Выход
""".format(version=__version__)

    while True:
        print(menu)
        choice = input("Выберите пункт: ").strip()
        try:
            if choice == "1":
                task = manager.create_task(
                    title=input("Название: "),
                    description=input("Описание: "),
                    priority=input("Приоритет (low/medium/high): "),
                    due_date=input("Срок (YYYY-MM-DD): "),
                )
                print("Задача добавлена:")
                _print_task(task)
            elif choice == "2":
                tasks = manager.list_tasks()
                if not tasks:
                    print("Задач нет")
                for task in tasks:
                    _print_task(task)
            elif choice == "3":
                tasks = manager.search_tasks(input("Поиск: "))
                if not tasks:
                    print("Ничего не найдено")
                for task in tasks:
                    _print_task(task)
            elif choice == "4":
                for task in manager.list_tasks(status=input("Статус (todo/done): ")):
                    _print_task(task)
            elif choice == "5":
                for task in manager.list_tasks(priority=input("Приоритет (low/medium/high): ")):
                    _print_task(task)
            elif choice == "6":
                task_id = _read_task_id()
                changes = {
                    "title": input("Новое название (пусто = оставить): ").strip() or None,
                    "description": input("Новое описание (пусто = оставить): ").strip() or None,
                    "priority": input("Новый приоритет (пусто = оставить): ").strip() or None,
                    "due_date": input("Новый срок YYYY-MM-DD (пусто = оставить): ").strip() or None,
                    "status": input("Новый статус todo/done (пусто = оставить): ").strip() or None,
                }
                task = manager.update_task(task_id, **changes)
                print("Задача обновлена:")
                _print_task(task)
            elif choice == "7":
                task = manager.mark_done(_read_task_id())
                print("Задача выполнена:")
                _print_task(task)
            elif choice == "8":
                manager.delete_task(_read_task_id())
                print("Задача удалена")
            elif choice == "9":
                reference_date = input("Дата проверки YYYY-MM-DD: ")
                tasks = manager.list_overdue(reference_date)
                if not tasks:
                    print("Просроченных задач нет")
                for task in tasks:
                    _print_task(task)
            elif choice == "0":
                print("Выход")
                break
            else:
                print("Неизвестный пункт меню")
        except (TaskValidationError, TaskNotFoundError) as exc:
            print(f"Ошибка: {exc}")

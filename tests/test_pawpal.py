"""Tests for pawpal_system.py core classes."""

from datetime import datetime

from pawpal_system import Pet, Priority, Task


def make_task(task_id: int = 1) -> Task:
    return Task(
        task_id=task_id,
        task_type="Walk",
        time=datetime.now(),
        duration_mins=20,
        priority=Priority.MEDIUM,
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(pet_id=1, name="Luna", species="Dog", age=4)
    assert len(pet.tasks) == 0

    pet.add_task(make_task())

    assert len(pet.tasks) == 1

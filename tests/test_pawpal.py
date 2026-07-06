"""Tests for pawpal_system.py core classes."""

from datetime import datetime, timedelta
from typing import Tuple

from pawpal_system import (
    Owner,
    Pet,
    Priority,
    RecurrenceInterval,
    Scheduler,
    Task,
)


def make_task(
    task_id: int = 1,
    time: datetime = None,
    priority: Priority = Priority.MEDIUM,
    is_recurring: bool = False,
    recurrence_interval: RecurrenceInterval = None,
    completed: bool = False,
    pet_id: int = None,
) -> Task:
    return Task(
        task_id=task_id,
        task_type="Walk",
        time=time if time is not None else datetime.now(),
        duration_mins=20,
        priority=priority,
        is_recurring=is_recurring,
        recurrence_interval=recurrence_interval,
        completed=completed,
        pet_id=pet_id,
    )


def make_owner_with_pet(pet_id: int = 1) -> Tuple[Owner, Pet, Scheduler]:
    pet = Pet(pet_id=pet_id, name="Luna", species="Dog", age=4)
    owner = Owner(owner_id=1, name="Jordan", pets=[pet])
    scheduler = Scheduler(owner)
    return owner, pet, scheduler


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


# --- Pet.get_upcoming_tasks --------------------------------------------------


def test_get_upcoming_tasks_empty_pet_returns_empty_list():
    pet = Pet(pet_id=1, name="Luna", species="Dog", age=4)

    assert pet.get_upcoming_tasks() == []


def test_get_upcoming_tasks_excludes_completed_tasks():
    pet = Pet(pet_id=1, name="Luna", species="Dog", age=4)
    pet.add_task(make_task(task_id=1, completed=True))
    pending = make_task(task_id=2, completed=False)
    pet.add_task(pending)

    assert pet.get_upcoming_tasks() == [pending]


def test_get_upcoming_tasks_sorted_earliest_to_latest():
    pet = Pet(pet_id=1, name="Luna", species="Dog", age=4)
    later = make_task(task_id=1, time=datetime(2026, 1, 2, 9, 0))
    earlier = make_task(task_id=2, time=datetime(2026, 1, 1, 9, 0))
    pet.add_task(later)
    pet.add_task(earlier)

    assert pet.get_upcoming_tasks() == [earlier, later]


def test_get_upcoming_tasks_preserves_insertion_order_for_equal_times():
    pet = Pet(pet_id=1, name="Luna", species="Dog", age=4)
    same_time = datetime(2026, 1, 1, 9, 0)
    first = make_task(task_id=1, time=same_time)
    second = make_task(task_id=2, time=same_time)
    pet.add_task(first)
    pet.add_task(second)

    assert pet.get_upcoming_tasks() == [first, second]


def test_get_upcoming_tasks_only_includes_this_pets_tasks():
    pet_a = Pet(pet_id=1, name="Luna", species="Dog", age=4)
    pet_b = Pet(pet_id=2, name="Milo", species="Cat", age=2)
    task_a = make_task(task_id=1, pet_id=1)
    task_b = make_task(task_id=2, pet_id=2)
    pet_a.add_task(task_a)
    pet_b.add_task(task_b)

    assert pet_a.get_upcoming_tasks() == [task_a]
    assert pet_b.get_upcoming_tasks() == [task_b]


# --- Scheduler.handle_recurrence ---------------------------------------------
#
# handle_recurrence() is a batch sweep: for every completed recurring task
# that hasn't already had a follow-up generated (whether by a prior sweep or
# by Scheduler.complete_task()), it generates and attaches the next
# occurrence. It must never generate a second follow-up for the same
# completed task.


def test_handle_recurrence_ignores_non_recurring_completed_tasks():
    _, pet, scheduler = make_owner_with_pet()
    pet.add_task(make_task(task_id=1, completed=True, is_recurring=False))

    scheduler.handle_recurrence()

    assert len(pet.tasks) == 1


def test_handle_recurrence_ignores_incomplete_recurring_tasks():
    _, pet, scheduler = make_owner_with_pet()
    pet.add_task(
        make_task(
            task_id=1,
            completed=False,
            is_recurring=True,
            recurrence_interval=RecurrenceInterval.DAILY,
        )
    )

    scheduler.handle_recurrence()

    assert len(pet.tasks) == 1


def test_handle_recurrence_generates_next_daily_occurrence():
    _, pet, scheduler = make_owner_with_pet()
    start = datetime(2026, 3, 10, 8, 0)
    task = make_task(
        task_id=1,
        time=start,
        completed=True,
        is_recurring=True,
        recurrence_interval=RecurrenceInterval.DAILY,
        pet_id=pet.pet_id,
    )
    pet.add_task(task)

    scheduler.handle_recurrence()

    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.time == start + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.task_id != task.task_id
    assert next_task.pet_id == pet.pet_id


def test_handle_recurrence_generates_next_weekly_occurrence():
    _, pet, scheduler = make_owner_with_pet()
    start = datetime(2026, 3, 10, 8, 0)
    task = make_task(
        task_id=1,
        time=start,
        completed=True,
        is_recurring=True,
        recurrence_interval=RecurrenceInterval.WEEKLY,
        pet_id=pet.pet_id,
    )
    pet.add_task(task)

    scheduler.handle_recurrence()

    assert pet.tasks[1].time == start + timedelta(weeks=1)


def test_handle_recurrence_rolls_over_month_boundary():
    _, pet, scheduler = make_owner_with_pet()
    start = datetime(2026, 1, 31, 8, 0)
    task = make_task(
        task_id=1,
        time=start,
        completed=True,
        is_recurring=True,
        recurrence_interval=RecurrenceInterval.DAILY,
        pet_id=pet.pet_id,
    )
    pet.add_task(task)

    scheduler.handle_recurrence()

    assert pet.tasks[1].time == datetime(2026, 2, 1, 8, 0)


def test_handle_recurrence_is_idempotent_across_repeated_calls():
    _, pet, scheduler = make_owner_with_pet()
    task = make_task(
        task_id=1,
        completed=True,
        is_recurring=True,
        recurrence_interval=RecurrenceInterval.DAILY,
        pet_id=pet.pet_id,
    )
    pet.add_task(task)

    scheduler.handle_recurrence()
    assert len(pet.tasks) == 2

    scheduler.handle_recurrence()
    assert len(pet.tasks) == 2


def test_handle_recurrence_does_not_duplicate_a_complete_task_followup():
    _, pet, scheduler = make_owner_with_pet()
    task = make_task(
        task_id=1,
        completed=False,
        is_recurring=True,
        recurrence_interval=RecurrenceInterval.DAILY,
        pet_id=pet.pet_id,
    )
    pet.add_task(task)

    scheduler.complete_task(task)
    assert len(pet.tasks) == 2

    scheduler.handle_recurrence()

    assert len(pet.tasks) == 2


def test_handle_recurrence_assigns_unique_ids_for_multiple_due_tasks():
    _, pet, scheduler = make_owner_with_pet()
    task_a = make_task(
        task_id=1,
        completed=True,
        is_recurring=True,
        recurrence_interval=RecurrenceInterval.DAILY,
        pet_id=pet.pet_id,
    )
    task_b = make_task(
        task_id=2,
        completed=True,
        is_recurring=True,
        recurrence_interval=RecurrenceInterval.WEEKLY,
        pet_id=pet.pet_id,
    )
    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler.handle_recurrence()

    ids = [t.task_id for t in pet.tasks]
    assert len(ids) == len(set(ids))


def test_handle_recurrence_skips_task_with_missing_pet():
    pet = Pet(pet_id=1, name="Luna", species="Dog", age=4)
    owner = Owner(owner_id=1, name="Jordan", pets=[pet])
    scheduler = Scheduler(owner)
    task = make_task(
        task_id=1,
        completed=True,
        is_recurring=True,
        recurrence_interval=RecurrenceInterval.DAILY,
        pet_id=999,  # no pet in the system has this id
    )
    pet.add_task(task)

    scheduler.handle_recurrence()  # must not raise

    assert len(pet.tasks) == 1

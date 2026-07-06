"""Demo script: build a small PawPal+ schedule and print today's tasks."""

from datetime import datetime

from pawpal_system import Owner, Pet, Priority, RecurrenceInterval, Scheduler, Task


def build_demo_owner() -> tuple[Owner, Scheduler]:
    luna = Pet(pet_id=1, name="Luna", species="Dog", age=4)
    milo = Pet(pet_id=2, name="Milo", species="Cat", age=2)

    owner = Owner(owner_id=1, name="Jordan")
    owner.add_pet(luna)
    owner.add_pet(milo)

    scheduler = Scheduler(owner)

    now = datetime.now()

    # Added out of chronological order (6pm, 7:30am, 9am, 12pm) on purpose,
    # to prove sort_by_time() actually reorders rather than just echoing
    # insertion order.
    dinner = Task(
        task_id=101,
        task_type="Feeding",
        time=now.replace(hour=18, minute=0, second=0, microsecond=0),
        duration_mins=15,
        priority=Priority.MEDIUM,
    )
    morning_walk = Task(
        task_id=102,
        task_type="Walk",
        time=now.replace(hour=7, minute=30, second=0, microsecond=0),
        duration_mins=30,
        priority=Priority.HIGH,
        is_recurring=True,
        recurrence_interval=RecurrenceInterval.DAILY,
    )
    vet_visit = Task(
        task_id=103,
        task_type="Vet visit",
        time=now.replace(hour=9, minute=0, second=0, microsecond=0),
        duration_mins=45,
        priority=Priority.HIGH,
    )
    brush_fur = Task(
        task_id=104,
        task_type="Grooming",
        time=now.replace(hour=12, minute=0, second=0, microsecond=0),
        duration_mins=10,
        priority=Priority.LOW,
    )

    scheduler.add_task(luna, dinner)
    scheduler.add_task(luna, morning_walk)
    scheduler.add_task(milo, vet_visit)
    scheduler.add_task(milo, brush_fur)

    return owner, scheduler


def print_tasks(title: str, owner: Owner, tasks: list[Task]) -> None:
    print(title)
    print("-" * 40)
    if not tasks:
        print("No matching tasks.")
        print()
        return
    for task in tasks:
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else "Unknown pet"
        time_str = task.time.strftime("%I:%M %p")
        status = "done" if task.completed else "pending"
        print(f"{time_str}  {pet_name:<8} {task.task_type:<12} ({task.priority.name}, {status})")
    print()


if __name__ == "__main__":
    owner, scheduler = build_demo_owner()

    print_tasks(
        "Today's tasks (chronological)",
        owner,
        sorted(scheduler.get_todays_tasks(), key=lambda t: t.time),
    )
    print_tasks("All tasks sorted by time", owner, scheduler.sort_by_time())
    print_tasks("All tasks sorted by priority", owner, scheduler.sort_by_priority())

    # morning_walk is a Daily recurring task. Completing it through the
    # scheduler (rather than calling task.mark_complete() directly) is what
    # triggers next_occurrence() and attaches tomorrow's walk automatically.
    morning_walk = next(t for t in owner.get_all_tasks() if t.task_type == "Walk")
    next_walk = scheduler.complete_task(morning_walk)
    if next_walk is not None:
        print(
            f"Completed '{morning_walk.task_type}' -> auto-scheduled next occurrence "
            f"on {next_walk.time.strftime('%A %I:%M %p')}"
        )
        print()

    print_tasks("Completed tasks", owner, scheduler.filter_tasks(completed=True))
    print_tasks("Pending tasks", owner, scheduler.filter_tasks(completed=False))
    print_tasks("Luna's tasks", owner, scheduler.filter_tasks(pet_name="Luna"))

    # Deliberately overlaps Milo's 9:00-9:45am vet visit, to prove
    # check_conflicts() catches same-time double-booking instead of letting
    # it through silently (or crashing).
    milo = next(p for p in owner.pets if p.name == "Milo")
    nail_trim = Task(
        task_id=105,
        task_type="Nail trim",
        time=datetime.now().replace(hour=9, minute=0, second=0, microsecond=0),
        duration_mins=15,
        priority=Priority.LOW,
    )
    warnings = scheduler.add_task(milo, nail_trim)

    print("Scheduling 'Nail trim' for Milo at 09:00 AM")
    print("-" * 40)
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    else:
        print("No conflicts found.")

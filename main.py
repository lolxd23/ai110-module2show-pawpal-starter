"""Demo script: build a small PawPal+ schedule and print today's tasks."""

from datetime import datetime

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def build_demo_owner() -> tuple[Owner, Scheduler]:
    luna = Pet(pet_id=1, name="Luna", species="Dog", age=4)
    milo = Pet(pet_id=2, name="Milo", species="Cat", age=2)

    owner = Owner(owner_id=1, name="Jordan")
    owner.add_pet(luna)
    owner.add_pet(milo)

    scheduler = Scheduler(owner)

    now = datetime.now()
    morning_walk = Task(
        task_id=101,
        task_type="Walk",
        time=now.replace(hour=7, minute=30, second=0, microsecond=0),
        duration_mins=30,
        priority=Priority.HIGH,
    )
    dinner = Task(
        task_id=102,
        task_type="Feeding",
        time=now.replace(hour=18, minute=0, second=0, microsecond=0),
        duration_mins=15,
        priority=Priority.MEDIUM,
    )
    brush_fur = Task(
        task_id=103,
        task_type="Grooming",
        time=now.replace(hour=12, minute=0, second=0, microsecond=0),
        duration_mins=10,
        priority=Priority.LOW,
    )

    scheduler.add_task(luna, morning_walk)
    scheduler.add_task(luna, dinner)
    scheduler.add_task(milo, brush_fur)

    return owner, scheduler


def print_todays_schedule(owner: Owner, scheduler: Scheduler) -> None:
    todays_tasks = sorted(scheduler.get_todays_tasks(), key=lambda t: t.time)

    print(f"Today's Schedule for {owner.name}")
    print("-" * 40)

    if not todays_tasks:
        print("No tasks scheduled for today.")
        return

    for task in todays_tasks:
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else "Unknown pet"
        time_str = task.time.strftime("%I:%M %p")
        print(f"{time_str}  {pet_name:<8} {task.task_type:<10} ({task.priority.name})")


if __name__ == "__main__":
    owner, scheduler = build_demo_owner()
    print_todays_schedule(owner, scheduler)

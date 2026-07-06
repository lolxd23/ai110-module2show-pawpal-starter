from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Tuple


class Priority(Enum):
    """Task urgency, ordered low to high."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class RecurrenceInterval(Enum):
    """How often a recurring task repeats."""

    DAILY = "Daily"
    WEEKLY = "Weekly"


@dataclass
class Task:
    """Represents a single pet care task (e.g. feeding, walk, medication, appointment)."""

    task_id: int
    task_type: str
    time: datetime
    duration_mins: int
    priority: Priority
    is_recurring: bool = False
    recurrence_interval: Optional[RecurrenceInterval] = None
    completed: bool = False
    pet_id: Optional[int] = None  # back-reference to the owning Pet

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_due_today(self, reference_date: Optional[date] = None) -> bool:
        """Return True if this task's date matches reference_date (defaults to today)."""
        target_date = reference_date if reference_date is not None else date.today()
        return self.time.date() == target_date

    def conflicts_with(self, other_task: "Task") -> bool:
        """Return True if this task's [time, time + duration_mins) window overlaps other_task's."""
        pass


@dataclass
class Pet:
    """Represents a pet profile and the tasks assigned to it."""

    pet_id: int
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append task to this pet's task list."""
        self.tasks.append(task)

    def get_upcoming_tasks(self) -> List[Task]:
        """Return this pet's incomplete tasks, ordered by time."""
        pass


class Owner:
    """Represents the pet owner; manages their pets and is the single source of
    truth for 'every task in the system' via get_all_tasks()."""

    def __init__(self, owner_id: int, name: str, pets: Optional[List[Pet]] = None) -> None:
        """Create an Owner with an id, name, and optional initial list of pets."""
        self.owner_id: int = owner_id
        self.name: str = name
        self.pets: List[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_pet(self, pet_id: int) -> Optional[Pet]:
        """Return the pet matching pet_id, or None if not found."""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets, flattened into one list."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    """Operates system-wide over an Owner's pets: prioritizes, detects
    conflicts, and manages recurrence.

    Holds a live reference to the Owner rather than a copied task list, so it
    never goes stale when pets/tasks are added after construction, and there's
    one source of truth (Owner.get_all_tasks()) instead of two.
    """

    def __init__(self, owner: Owner) -> None:
        """Create a Scheduler bound to a live Owner reference."""
        self.owner: Owner = owner

    def add_task(self, pet: Pet, task: Task) -> None:
        """Attach task to pet, making it visible system-wide immediately."""
        task.pet_id = pet.pet_id
        pet.add_task(task)

    def sort_by_priority(self) -> List[Task]:
        """Return all tasks ordered from highest to lowest priority."""
        return sorted(self.owner.get_all_tasks(), key=lambda t: t.priority.value, reverse=True)

    def detect_conflicts(self) -> List[Tuple[Task, Task]]:
        """Return all pairs of tasks whose time windows overlap."""
        tasks = self.owner.get_all_tasks()
        return [
            (a, b)
            for i, a in enumerate(tasks)
            for b in tasks[i + 1:]
            if a.conflicts_with(b)
        ]

    def get_todays_tasks(self) -> List[Task]:
        """Return all tasks due today."""
        return [t for t in self.owner.get_all_tasks() if t.is_due_today()]

    def handle_recurrence(self) -> None:
        """Generate and reattach the next occurrence of each due recurring task."""
        pass

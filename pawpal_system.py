from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Task:
    """Represents a single pet care task (e.g. feeding, walk, medication, appointment)."""

    task_type: str
    time: datetime
    is_recurring: bool
    recurrence_interval: str
    priority: int
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def is_due_today(self) -> bool:
        pass

    def conflicts_with(self, other_task: "Task") -> bool:
        pass


@dataclass
class Pet:
    """Represents a pet profile and the tasks assigned to it."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def get_upcoming_tasks(self) -> List[Task]:
        pass


class Owner:
    """Represents the pet owner; manages their pets and aggregates tasks across all of them."""

    def __init__(self, name: str, pets: Optional[List[Pet]] = None) -> None:
        self.name: str = name
        self.pets: List[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass


class Scheduler:
    """Operates system-wide across tasks: prioritizes, detects conflicts, and manages recurrence."""

    def __init__(self, tasks: Optional[List[Task]] = None) -> None:
        self.tasks: List[Task] = tasks if tasks is not None else []

    def sort_by_priority(self) -> List[Task]:
        pass

    def detect_conflicts(self) -> List[tuple]:
        pass

    def get_todays_tasks(self) -> List[Task]:
        pass

    def handle_recurrence(self) -> None:
        pass

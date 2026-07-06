from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """Base class for a single pet care activity (e.g. feeding, walk, grooming)."""

    task_id: int
    title: str
    due_time: datetime
    duration_mins: int = 15
    priority: Priority = Priority.MEDIUM
    is_completed: bool = False
    frequency: str = "Once"  # Once, Daily, Weekly
    is_flexible: bool = True  # can Scheduler move this task's time?

    def mark_complete(self) -> None:
        """TODO: mark this task as done."""
        pass

    def get_end_time(self) -> datetime:
        """TODO: return due_time + duration_mins."""
        pass

    def overlaps_with(self, other: "Task") -> bool:
        """TODO: pure time-window comparison against another task.
        Should only compare self/other's due_time and duration - no
        knowledge of the wider schedule belongs here."""
        pass

    def next_occurrence(self) -> Optional["Task"]:
        """TODO: if frequency is Daily/Weekly, return the next instance
        of this task. Return None for a one-off task."""
        pass


@dataclass
class Medication(Task):
    """A task requiring a specific dose of medicine on a fixed schedule."""

    medication_name: str = ""
    dosage: str = ""
    refill_date: Optional[datetime] = None
    requires_food: bool = False
    is_flexible: bool = False  # dosing times are not freely reschedulable

    def is_refill_needed(self) -> bool:
        """TODO: compare refill_date to today."""
        pass


@dataclass
class Appointment(Task):
    """A task tied to an external, fixed-time commitment (vet, groomer, etc.)."""

    location: str = ""
    provider_name: str = ""
    appointment_type: str = ""
    travel_buffer_mins: int = 0
    is_flexible: bool = False  # externally fixed time

    def get_departure_time(self) -> datetime:
        """TODO: return due_time - travel_buffer_mins."""
        pass

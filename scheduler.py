from dataclasses import dataclass, field
from datetime import date
from typing import List, Tuple

from pet import Pet
from task import Task


@dataclass
class Scheduler:
    """Operates system-wide across all pets/tasks. Holds no pet-specific
    data of its own beyond the pets it's been given to schedule for."""

    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """TODO: register a pet with the scheduler."""
        pass

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        """TODO: return (pet_name, task) tuples across all pets."""
        pass

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """TODO: order tasks by priority, then due_time."""
        pass

    def check_conflicts(self, new_task: Task) -> bool:
        """TODO: use Task.overlaps_with() against every existing task
        system-wide to decide whether new_task conflicts with anything."""
        pass

    def generate_daily_plan(self, target_date: date) -> List[Task]:
        """TODO: anchor fixed tasks (Medication/Appointment, is_flexible=False),
        then place flexible tasks around them by priority, avoiding conflicts."""
        pass

    def generate_recurring_tasks(self) -> None:
        """TODO: call Task.next_occurrence() for due recurring tasks and
        add the results back to the owning pet."""
        pass

    def explain_plan(self, plan: List[Task]) -> List[str]:
        """TODO: return a human-readable reason string per task in the plan."""
        pass

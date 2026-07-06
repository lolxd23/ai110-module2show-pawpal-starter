from dataclasses import dataclass, field
from typing import List

from task import Task


@dataclass
class Pet:
    """A pet profile belonging to an Owner."""

    pet_id: int
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """TODO: append task to self.tasks."""
        pass

    def remove_task(self, task_id: int) -> None:
        """TODO: remove a task by id."""
        pass

    def get_incomplete_tasks(self) -> List[Task]:
        """TODO: filter self.tasks for is_completed == False."""
        pass

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
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
        """Mark this task as completed.

        Returns:
            None.
        """
        self.completed = True

    def is_due_today(self, reference_date: Optional[date] = None) -> bool:
        """Check whether this task's date matches a reference date.

        Args:
            reference_date: The date to compare against. Defaults to
                today's date when omitted.

        Returns:
            True if this task's date matches reference_date, else False.
        """
        target_date = reference_date if reference_date is not None else date.today()
        return self.time.date() == target_date

    def conflicts_with(self, other_task: "Task") -> bool:
        """Check whether this task's time window overlaps another task's.

        Args:
            other_task: The task to compare this task's window against.

        Returns:
            True if this task's [time, time + duration_mins) window overlaps
            other_task's, else False.

        Note:
            O(1) - a fixed number of datetime comparisons regardless of how
            many tasks exist in the system.
        """
        self_end = self.time + timedelta(minutes=self.duration_mins)
        other_end = other_task.time + timedelta(minutes=other_task.duration_mins)
        return self.time < other_end and other_task.time < self_end

    def next_occurrence(self, new_task_id: int) -> "Task":
        """Build the next occurrence of this recurring task.

        A Daily task moves forward by exactly one day and a Weekly task by
        exactly one week; timedelta does that arithmetic correctly across
        month/year boundaries (e.g. Jan 31 + 1 day -> Feb 1), which manually
        incrementing date parts would get wrong.

        Args:
            new_task_id: The task_id to assign to the newly created Task,
                since ids must stay unique across the system.

        Returns:
            A new, incomplete Task with the same type/duration/priority as
            this one, scheduled at the next occurrence time.

        Raises:
            ValueError: If this task isn't recurring, has no
                recurrence_interval set, or has an unsupported interval.
        """
        if not self.is_recurring or self.recurrence_interval is None:
            raise ValueError("next_occurrence() requires a recurring task with an interval set")

        if self.recurrence_interval is RecurrenceInterval.DAILY:
            delta = timedelta(days=1)
        elif self.recurrence_interval is RecurrenceInterval.WEEKLY:
            delta = timedelta(weeks=1)
        else:
            raise ValueError(f"Unsupported recurrence interval: {self.recurrence_interval!r}")

        return Task(
            task_id=new_task_id,
            task_type=self.task_type,
            time=self.time + delta,
            duration_mins=self.duration_mins,
            priority=self.priority,
            is_recurring=self.is_recurring,
            recurrence_interval=self.recurrence_interval,
            completed=False,
            pet_id=self.pet_id,
        )


@dataclass
class Pet:
    """Represents a pet profile and the tasks assigned to it."""

    pet_id: int
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append task to this pet's task list.

        Args:
            task: The task to attach to this pet.

        Returns:
            None.
        """
        self.tasks.append(task)

    def get_upcoming_tasks(self) -> List[Task]:
        """Return this pet's incomplete tasks, ordered by time.

        Returns:
            This pet's tasks where completed is False, sorted earliest to
            latest by time.

        Note:
            O(n log n) - filters this pet's own tasks, then sorts. n here
            is just this pet's task count, not every task in the system.
            sorted() is stable, so tasks with equal times keep their
            original insertion order.
        """
        return sorted(
            (t for t in self.tasks if not t.completed),
            key=lambda t: t.time,
        )


class Owner:
    """Represents the pet owner; manages their pets and is the single source of
    truth for 'every task in the system' via get_all_tasks()."""

    def __init__(self, owner_id: int, name: str, pets: Optional[List[Pet]] = None) -> None:
        """Create an Owner.

        Args:
            owner_id: Unique identifier for this owner.
            name: The owner's display name.
            pets: Initial list of pets this owner has. Defaults to an empty
                list when omitted.

        Returns:
            None.
        """
        self.owner_id: int = owner_id
        self.name: str = name
        self.pets: List[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add pet to this owner's list of pets.

        Args:
            pet: The pet to add.

        Returns:
            None.
        """
        self.pets.append(pet)

    def get_pet(self, pet_id: int) -> Optional[Pet]:
        """Look up one of this owner's pets by id.

        Args:
            pet_id: The pet_id to search for.

        Returns:
            The matching Pet, or None if no pet with that id belongs to
            this owner.

        Note:
            O(n) - linear scan over self.pets. Fine at the scale of one
            owner's pets, but called once per task in a few Scheduler
            methods (e.g. filter_tasks, check_conflicts), so it's worth
            keeping in mind if pet counts ever grow large.
        """
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Flatten every task across all of this owner's pets into one list.

        Returns:
            A new list containing every task from every pet this owner has,
            in pet order and then each pet's own task order.

        Note:
            O(n) where n = total tasks across all pets - each pet's task
            list is walked once and appended to the result.
        """
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
        """Create a Scheduler bound to a live Owner reference.

        Args:
            owner: The Owner this scheduler operates over. Held by
                reference so the scheduler never goes stale when pets/tasks
                are added after construction.

        Returns:
            None.
        """
        self.owner: Owner = owner

    def add_task(self, pet: Pet, task: Task) -> List[str]:
        """Attach task to pet, making it visible system-wide immediately.

        Conflicts are surfaced as warnings, not exceptions - adding a
        clashing task still succeeds, it's up to the caller (UI, script,
        etc.) to decide what to do with the warning.

        Args:
            pet: The pet this task belongs to.
            task: The task to schedule. Its pet_id is set to pet.pet_id as
                a side effect.

        Returns:
            Conflict warnings found against already-scheduled tasks (see
            check_conflicts), checked before this task is attached so it's
            never compared against itself. Empty list if there's no conflict.

        Note:
            O(n) - dominated by the check_conflicts() call it makes before
            attaching the task.
        """
        warnings = self.check_conflicts(task)
        task.pet_id = pet.pet_id
        pet.add_task(task)
        return warnings

    def check_conflicts(self, new_task: Task) -> List[str]:
        """Lightweight conflict check for a single task against everything scheduled.

        Compares new_task against each existing task once - no need to sort
        or compare every pair in the system the way detect_conflicts() does
        for a full system-wide report - and returns a human-readable warning
        per overlap instead of raising.

        Args:
            new_task: The task to check for conflicts. Excluded from the
                comparison if it's already attached to a pet.

        Returns:
            One warning string per conflicting existing task, or an empty
            list when there's no conflict.

        Note:
            O(n) - one pass over every existing task in the system, versus
            detect_conflicts()'s O(n log n) sort for a full pairwise report.
        """
        warnings: List[str] = []
        for existing in self.owner.get_all_tasks():
            if existing is new_task:
                continue
            if new_task.conflicts_with(existing):
                pet = self.owner.get_pet(existing.pet_id)
                pet_name = pet.name if pet else "an unknown pet"
                time_str = existing.time.strftime("%I:%M %p")
                warnings.append(
                    f"Conflict: '{new_task.task_type}' overlaps with {pet_name}'s "
                    f"'{existing.task_type}' at {time_str}"
                )
        return warnings

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark task complete, and if it's recurring, spawn and attach its next occurrence.

        Completion and recurrence are tied together here (rather than on
        Task.mark_complete() itself) because generating the next occurrence
        needs a fresh task_id and the owning Pet to attach it to - both of
        which only the Scheduler has visibility into system-wide.

        Args:
            task: The task to mark complete.

        Returns:
            The newly created follow-up task, or None if task isn't
            recurring (or its owning pet can't be found).

        Note:
            O(n) - dominated by the _next_task_id() and get_pet() lookups it
            performs when the task is recurring.
        """
        task.mark_complete()

        if not task.is_recurring or task.recurrence_interval is None:
            return None

        pet = self.owner.get_pet(task.pet_id)
        if pet is None:
            return None

        next_task = task.next_occurrence(new_task_id=self._next_task_id())
        pet.add_task(next_task)
        task.is_recurring = False  # this occurrence has already spawned its follow-up
        return next_task

    def _next_task_id(self) -> int:
        """Compute the next unique task id.

        Returns an id one higher than the current max, so ids stay unique
        even after tasks are completed/removed (unlike len(tasks) + 1).

        Returns:
            max(existing task_id across the system, default 0) + 1.

        Note:
            O(n) - scans every task once to find the current max id.
        """
        existing_ids = [t.task_id for t in self.owner.get_all_tasks()]
        return max(existing_ids, default=0) + 1

    def sort_by_priority(self) -> List[Task]:
        """Order all tasks from highest to lowest priority.

        Returns:
            Every task in the system, sorted by priority descending
            (HIGH first, LOW last).

        Note:
            O(n log n) - a single sort over all tasks in the system.
        """
        return sorted(self.owner.get_all_tasks(), key=lambda t: t.priority.value, reverse=True)

    def sort_by_time(self) -> List[Task]:
        """Order all tasks earliest to latest by their time attribute.

        Returns:
            Every task in the system, sorted chronologically ascending.

        Note:
            O(n log n) - a single sort over all tasks in the system.
        """
        return sorted(self.owner.get_all_tasks(), key=lambda t: t.time)

    def filter_tasks(
        self, completed: Optional[bool] = None, pet_name: Optional[str] = None
    ) -> List[Task]:
        """Return tasks matching the given completion status and/or pet name.

        Both filters are optional and combine with AND: pass only one to
        filter on just that criterion, or both to narrow by both at once.
        Passing neither returns every task.

        Args:
            completed: If given, keep only tasks whose completed attribute
                equals this value.
            pet_name: If given, keep only tasks belonging to the pet with
                this name.

        Returns:
            The tasks matching every filter that was provided.

        Note:
            O(n) for the completed filter. The pet_name filter adds an
            Owner.get_pet() lookup per task, which is itself O(p) (p =
            number of pets), so filtering by pet_name is O(n*p) worst case -
            negligible for one owner's pet count, but worth knowing if that
            ever changes.
        """
        tasks = self.owner.get_all_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [
                t
                for t in tasks
                if (pet := self.owner.get_pet(t.pet_id)) is not None and pet.name == pet_name
            ]
        return tasks

    def detect_conflicts(self) -> List[Tuple[Task, Task]]:
        """Find every pair of scheduled tasks whose time windows overlap.

        Sorts tasks by start time first (sweep-line), so each task only needs
        to be checked against the tasks immediately following it: once a
        later task starts at or after the current task's end time, every
        task after that (all starting even later) can't overlap it either,
        so the inner loop breaks early instead of scanning the rest.

        Returns:
            A list of (task_a, task_b) tuples, one per overlapping pair,
            with task_a always starting no later than task_b.

        Note:
            O(n log n) to sort, then an amortized near-linear sweep in the
            common case where few tasks overlap (the inner loop breaks
            early). Worst case is still O(n^2) if most tasks overlap each
            other, since then the early break rarely triggers.
        """
        tasks = sorted(self.owner.get_all_tasks(), key=lambda t: t.time)
        conflicts: List[Tuple[Task, Task]] = []
        for i, a in enumerate(tasks):
            a_end = a.time + timedelta(minutes=a.duration_mins)
            for b in tasks[i + 1:]:
                if b.time >= a_end:
                    break
                if a.conflicts_with(b):
                    conflicts.append((a, b))
        return conflicts

    def get_todays_tasks(self) -> List[Task]:
        """Return all tasks due today.

        Returns:
            Every task in the system whose is_due_today() is True.

        Note:
            O(n) - one pass over every task in the system.
        """
        return [t for t in self.owner.get_all_tasks() if t.is_due_today()]

    def handle_recurrence(self) -> None:
        """Generate and reattach the next occurrence of each due recurring task.

        A task qualifies once it's completed, is_recurring is True, and it
        has a recurrence_interval set. After generating its follow-up, the
        original task's is_recurring flag is flipped to False so a repeated
        call to handle_recurrence() won't spawn a second follow-up for the
        same completed task - that's what makes this method idempotent.

        Returns:
            None.

        Note:
            O(n) - one pass over every task to find due recurring ones,
            then one next_occurrence() call (O(1)) per match.
        """
        for task in self.owner.get_all_tasks():
            if task.completed and task.is_recurring and task.recurrence_interval is not None:
                pet = self.owner.get_pet(task.pet_id)
                if pet is None:
                    continue
                next_task = task.next_occurrence(new_task_id=self._next_task_id())
                pet.add_task(next_task)
                task.is_recurring = False  # prevents regenerating on a later call
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum


class Priority(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Pet:
    pet_id: int
    name: str
    owner_id: int
    species: str
    dietary_preferences: list[str] = field(default_factory=list)
    tasks: list["Task"] = field(default_factory=list)

    def change_owner(self, owner_id: int) -> None:
        """Update the pet's owner to a new owner ID."""
        self.owner_id = owner_id

    def complete_task(self, task: "Task") -> "Task | None":
        """Mark a task complete and handle recurrence for this pet.

        Calls task.mark_complete(). If the task is recurring ("daily" or
        "weekly"), the newly created next-occurrence Task is automatically
        appended to this pet's tasks list.

        Args:
            task: The Task instance to mark as completed.

        Returns:
            The next-occurrence Task if the task is recurring, otherwise None.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)
        return next_task


@dataclass
class Task:
    task_id: int
    task_name: str
    is_completed: bool
    duration: int
    time: int
    priority: Priority
    pet_id: int
    recurrence: str = None       # None, "daily", or "weekly"
    due_date: date = None        # when this task is due

    def mark_complete(self) -> "Task | None":
        """Mark this task as completed.

        For recurring tasks ("daily" or "weekly"), returns a new Task
        instance whose due_date is shifted forward by the appropriate
        timedelta. Returns None for non-recurring tasks.
        """
        self.is_completed = True

        if self.recurrence not in ("daily", "weekly"):
            return None

        days_ahead = 1 if self.recurrence == "daily" else 7
        next_due = (self.due_date or date.today()) + timedelta(days=days_ahead)

        return Task(
            task_id=self.task_id + 1000,
            task_name=self.task_name,
            is_completed=False,
            duration=self.duration,
            time=self.time,
            priority=self.priority,
            pet_id=self.pet_id,
            recurrence=self.recurrence,
            due_date=next_due,
        )

    def edit_task(self, task_name: str, duration: int, time: int, priority: Priority) -> None:
        """Update the task's name, duration, time, and priority."""
        self.task_name = task_name
        self.duration = duration
        self.time = time
        self.priority = priority


class Owner:
    def __init__(self, owner_id: int, name: str, email: str, phone_number: str, available_time: int):
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.available_time = available_time
        self.preferred_tasks: list[str] = []
        self.favorite_pets: list[Pet] = []
        self.current_pets: list[Pet] = []

    def add_current_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's current pets list."""
        self.current_pets.append(pet)

    def remove_current_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's current pets list."""
        self.current_pets.remove(pet)

    def add_favorite_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's favorites list."""
        self.favorite_pets.append(pet)

    def remove_favorite_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's favorites list."""
        self.favorite_pets.remove(pet)

    def change_email(self, new_email: str) -> None:
        """Update the owner's email address."""
        self.email = new_email

    def get_all_tasks(self) -> list["Task"]:
        """Collect and return all tasks across the owner's current pets.

        Iterates through each pet in current_pets and aggregates their
        task lists into a single flat list.

        Returns:
            A list of all Task instances belonging to the owner's pets.
        """
        tasks = []
        for pet in self.current_pets:
            tasks.extend(pet.tasks)
        return tasks

    def filter_tasks(self, pet_name: str = None, completed: bool = None) -> list["Task"]:
        """Filter tasks by pet name and/or completion status.

        Args:
            pet_name: If provided, only return tasks belonging to this pet.
            completed: If provided, only return tasks matching this completion status.
                       True = completed only, False = incomplete only, None = all.
        """
        tasks = []
        for pet in self.current_pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            tasks.extend(pet.tasks)

        if completed is not None:
            tasks = [t for t in tasks if t.is_completed == completed]

        return tasks


class Schedule:
    def __init__(self):
        self.schedule: list[Task] = []
        self.total_time: int = 0
        self.explanation: str = ""

    def generate_schedule(self, tasks: list[Task], available_time: int, preferred_tasks: list[str] = None) -> "Schedule":
        """Generate an optimized daily schedule that fits within available time.

        Tasks are sorted by a three-level key:
          1. Priority (HIGH > MEDIUM > LOW)
          2. Owner preference (preferred task names come first as tiebreaker)
          3. Time of day (earlier hours scheduled first)

        A greedy algorithm then walks the sorted list, adding each incomplete
        task if its duration fits within the remaining available time.
        Completed tasks are skipped automatically. After scheduling, a
        conflict check flags any tasks sharing the same time slot.

        Args:
            tasks: All candidate Task instances to consider.
            available_time: Maximum minutes the owner has for pet care today.
            preferred_tasks: Optional list of task names the owner prefers.

        Returns:
            self, with schedule, total_time, and explanation populated.
        """
        if preferred_tasks is None:
            preferred_tasks = []

        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                priority_order[t.priority],
                0 if t.task_name in preferred_tasks else 1,
                t.time,
            ),
        )

        self.schedule = []
        self.total_time = 0
        reasons = []

        for task in sorted_tasks:
            if task.is_completed:
                reasons.append(f"Skipped '{task.task_name}' — already completed")
                continue
            if self.total_time + task.duration <= available_time:
                self.schedule.append(task)
                self.total_time += task.duration
                reasons.append(f"Added '{task.task_name}' ({task.priority.value} priority, {task.duration} min)")
            else:
                reasons.append(f"Skipped '{task.task_name}' — not enough time remaining")

        # Detect time-slot conflicts among scheduled tasks
        warnings = self._detect_conflicts()

        self.explanation = (
            f"Scheduled {len(self.schedule)} task(s) within {available_time} min.\n"
            + "Tasks sorted by priority (HIGH > MEDIUM > LOW), "
            + "preferred tasks as tiebreaker, then by time of day.\n"
            + "\n".join(reasons)
        )
        if warnings:
            self.explanation += "\n\nConflict warnings:\n" + "\n".join(warnings)

        return self

    def _detect_conflicts(self) -> list[str]:
        """Check scheduled tasks for exact time-slot collisions.

        Compares every pair of scheduled tasks. If two tasks share the
        same time value (hour of day), a warning string is generated.
        Note: this checks for exact hour matches only, not duration-based
        overlap (see reflection.md section 2b for the tradeoff rationale).

        Returns:
            A list of human-readable warning strings, empty if no conflicts.
        """
        warnings = []
        for i, a in enumerate(self.schedule):
            for b in self.schedule[i + 1:]:
                if a.time == b.time:
                    warnings.append(
                        f"  ⚠ '{a.task_name}' and '{b.task_name}' are both scheduled at {a.time}:00"
                    )
        return warnings

    def get_tasks(self) -> list[Task]:
        """Return the list of scheduled tasks."""
        return self.schedule

    def get_explanation(self) -> str:
        """Return the explanation of scheduling decisions."""
        return self.explanation

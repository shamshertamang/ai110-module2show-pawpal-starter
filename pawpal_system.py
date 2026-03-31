from dataclasses import dataclass, field
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


@dataclass
class Task:
    task_id: int
    task_name: str
    is_completed: bool
    duration: int
    time: int
    priority: Priority
    pet_id: int

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

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


class Schedule:
    def __init__(self):
        self.schedule: list[Task] = []
        self.total_time: int = 0
        self.explanation: str = ""

    def generate_schedule(self, tasks: list[Task], available_time: int, preferred_tasks: list[str] = None) -> "Schedule":
        """Generate an optimized daily schedule sorted by priority within available time."""
        if preferred_tasks is None:
            preferred_tasks = []

        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                priority_order[t.priority],
                0 if t.task_name in preferred_tasks else 1,
            ),
        )

        self.schedule = []
        self.total_time = 0
        reasons = []

        for task in sorted_tasks:
            if self.total_time + task.duration <= available_time:
                self.schedule.append(task)
                self.total_time += task.duration
                reasons.append(f"Added '{task.task_name}' ({task.priority.value} priority, {task.duration} min)")
            else:
                reasons.append(f"Skipped '{task.task_name}' — not enough time remaining")

        self.explanation = (
            f"Scheduled {len(self.schedule)} task(s) within {available_time} min.\n"
            + "Tasks sorted by priority (HIGH > MEDIUM > LOW), "
            + "with preferred tasks as tiebreaker.\n"
            + "\n".join(reasons)
        )

        return self

    def get_tasks(self) -> list[Task]:
        """Return the list of scheduled tasks."""
        return self.schedule

    def get_explanation(self) -> str:
        """Return the explanation of scheduling decisions."""
        return self.explanation

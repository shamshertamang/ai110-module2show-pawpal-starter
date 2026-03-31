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

    def change_owner(self, owner_id: int) -> None:
        pass


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
        pass


class Owner:
    def __init__(self, owner_id: int, name: str, email: str, phone_number: str, available_time: int):
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.available_time = available_time
        self.favorite_pets: list[Pet] = []
        self.current_pets: list[Pet] = []

    def add_current_pet(self, pet: Pet) -> None:
        pass

    def remove_current_pet(self, pet: Pet) -> None:
        pass

    def add_favorite_pet(self, pet: Pet) -> None:
        pass

    def remove_favorite_pet(self, pet: Pet) -> None:
        pass

    def change_email(self, new_email: str) -> None:
        pass


class Schedule:
    def __init__(self):
        self.schedule: list[Task] = []
        self.total_time: int = 0

    def generate_schedule(self, tasks: list[Task], available_time: int) -> "Schedule":
        pass

    def get_tasks(self) -> list[Task]:
        pass

"""
PawPal+ System — Logic Layer
Defines the core classes: Task, Pet, Owner, and Scheduler.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List


@dataclass
class Task:
    """Represents a single care activity for a pet."""
    description: str
    time: str                        # Format: "HH:MM"
    frequency: str = "once"          # "once", "daily", or "weekly"
    is_complete: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self):
        """Mark this task as complete."""
        self.is_complete = True

    def is_recurring(self) -> bool:
        """Return True if this task repeats (daily or weekly)."""
        return self.frequency in ("daily", "weekly")


@dataclass
class Pet:
    """Represents a pet owned by an Owner."""
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from this pet's task list."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that are not yet complete."""
        return [t for t in self.tasks if not t.is_complete]


class Owner:
    """Represents a pet owner who manages one or more pets."""

    def __init__(self, name: str, email: str = ""):
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's collection."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    """The brain of PawPal+. Retrieves and organizes tasks for an Owner."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Retrieve every task across all pets from the owner."""
        return self.owner.get_all_tasks()

    def sort_by_time(self) -> List[Task]:
        """Return all tasks sorted chronologically by their time attribute."""
        return sorted(self.get_all_tasks(), key=lambda t: t.time)

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return tasks belonging to a specific pet."""
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.tasks
        return []

    def filter_by_status(self, complete: bool) -> List[Task]:
        """Return tasks filtered by completion status."""
        return [t for t in self.get_all_tasks() if t.is_complete == complete]

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for tasks scheduled at the same time for the same pet."""
        warnings = []
        for pet in self.owner.pets:
            seen_times = {}
            for task in pet.tasks:
                if task.time in seen_times:
                    warnings.append(
                        f"⚠️ Conflict for {pet.name}: '{task.description}' and "
                        f"'{seen_times[task.time]}' are both scheduled at {task.time}"
                    )
                else:
                    seen_times[task.time] = task.description
        return warnings

    def handle_recurring(self, task: Task, pet: Pet):
        """When a recurring task is completed, create the next occurrence and add it to the pet."""
        if not task.is_recurring():
            return
        if task.frequency == "daily":
            next_date = task.due_date + timedelta(days=1)
        else:  # weekly
            next_date = task.due_date + timedelta(weeks=1)

        new_task = Task(
            description=task.description,
            time=task.time,
            frequency=task.frequency,
            is_complete=False,
            due_date=next_date,
        )
        pet.add_task(new_task)
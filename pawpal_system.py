"""PawPal+ scheduling system — Owner, Pet, Task, and Scheduler classes."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single care task for a pet."""

    description: str
    time: str                          # "HH:MM" 24-hour string
    frequency: str = "once"            # "once" | "daily" | "weekly"
    is_complete: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> "Task | None":
        """Mark this task complete; return a successor Task for recurring tasks or None.

        Returns:
            A new Task with the next due date for daily/weekly tasks, or None for once tasks.
        """
        if self.frequency == "once":
            self.is_complete = True
            return None
        elif self.frequency == "daily":
            return Task(
                description=self.description,
                time=self.time,
                frequency=self.frequency,
                is_complete=False,
                due_date=self.due_date + timedelta(days=1),
            )
        elif self.frequency == "weekly":
            return Task(
                description=self.description,
                time=self.time,
                frequency=self.frequency,
                is_complete=False,
                due_date=self.due_date + timedelta(days=7),
            )
        return None


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents a pet belonging to an owner."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a Task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """Represents a pet owner who manages one or more pets."""

    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list:
        """Return all tasks across all pets as a flat list of dicts with pet name attached."""
        result = []
        for pet_index, pet in enumerate(self.pets):
            for task_index, task in enumerate(pet.tasks):
                result.append({
                    "pet_name": pet.name,
                    "pet_index": pet_index,
                    "task_index": task_index,
                    "description": task.description,
                    "time": task.time,
                    "frequency": task.frequency,
                    "is_complete": task.is_complete,
                    "due_date": task.due_date,
                })
        return result


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Service class that provides scheduling operations for an Owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with an Owner instance."""
        self.owner = owner

    def get_todays_schedule(self) -> list:
        """Return all incomplete tasks due today across all pets as a list of dicts."""
        today = date.today()
        result = []
        for pet_index, pet in enumerate(self.owner.pets):
            for task_index, task in enumerate(pet.tasks):
                if task.due_date == today and not task.is_complete:
                    result.append({
                        "pet_name": pet.name,
                        "pet_index": pet_index,
                        "task_index": task_index,
                        "description": task.description,
                        "time": task.time,
                        "frequency": task.frequency,
                        "is_complete": task.is_complete,
                        "due_date": task.due_date,
                    })
        return result

    def sort_by_time(self, tasks: list) -> list:
        """Return tasks sorted chronologically by HH:MM time string."""
        return sorted(tasks, key=lambda t: t["time"])

    def filter_tasks(self, tasks: list, pet_name: str = None, completed: bool = None) -> list:
        """Return tasks filtered by optional pet name and/or completion status."""
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t["pet_name"] == pet_name]
        if completed is not None:
            result = [t for t in result if t["is_complete"] == completed]
        return result

    def detect_conflicts(self, tasks: list) -> list:
        """Return a list of warning strings for tasks that share the same time slot."""
        by_time = defaultdict(list)
        for t in tasks:
            by_time[t["time"]].append(t)

        warnings = []
        for time_slot, conflicting in by_time.items():
            if len(conflicting) > 1:
                names = " and ".join(
                    f'{t["description"]} ({t["pet_name"]})' for t in conflicting
                )
                warnings.append(f"Conflict at {time_slot}: {names}")
        return warnings

    def handle_recurring(self, task: Task) -> "Task | None":
        """Handle recurrence logic for a task; returns successor Task or None."""
        return task.mark_complete()

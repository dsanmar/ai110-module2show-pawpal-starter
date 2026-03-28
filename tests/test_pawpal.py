"""Pytest tests for PawPal+ scheduling system."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_once():
    """mark_complete() on a 'once' task sets is_complete=True and returns None."""
    task = Task(description="Give flea treatment", time="10:00", frequency="once")
    result = task.mark_complete()
    assert task.is_complete is True
    assert result is None


def test_mark_complete_daily_returns_new_task():
    """mark_complete() on a 'daily' task returns a new Task due tomorrow."""
    today = date.today()
    task = Task(description="Morning walk", time="09:00", frequency="daily", due_date=today)
    successor = task.mark_complete()
    assert successor is not None
    assert successor.due_date == today + timedelta(days=1)
    assert successor.is_complete is False
    assert successor.frequency == "daily"
    # original task should be unchanged (mark_complete does NOT mutate recurring tasks)
    assert task.is_complete is False


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    """Adding a task to a pet increases its task list length by 1."""
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(description="Morning walk", time="08:00"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task(description="Evening feeding", time="18:00"))
    assert len(pet.get_tasks()) == 2


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def _make_schedule_dict(pet_name, description, time_str, pet_index=0, task_index=0):
    """Helper — build the dict format Scheduler methods use."""
    return {
        "pet_name": pet_name,
        "pet_index": pet_index,
        "task_index": task_index,
        "description": description,
        "time": time_str,
        "frequency": "once",
        "is_complete": False,
        "due_date": date.today(),
    }


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() returns tasks in HH:MM chronological order."""
    owner = Owner(name="Alex")
    scheduler = Scheduler(owner)

    tasks = [
        _make_schedule_dict("Buddy", "Evening feeding", "18:00"),
        _make_schedule_dict("Buddy", "Morning walk", "09:00"),
        _make_schedule_dict("Whiskers", "Vet check-up", "11:00"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)
    times = [t["time"] for t in sorted_tasks]
    assert times == ["09:00", "11:00", "18:00"]


def test_detect_conflicts_catches_same_time():
    """detect_conflicts() returns warning strings when two tasks share a time slot."""
    owner = Owner(name="Alex")
    scheduler = Scheduler(owner)

    tasks = [
        _make_schedule_dict("Buddy",    "Morning walk",    "09:00", pet_index=0, task_index=0),
        _make_schedule_dict("Whiskers", "Morning feeding", "09:00", pet_index=1, task_index=0),
    ]

    conflicts = scheduler.detect_conflicts(tasks)
    assert len(conflicts) == 1
    assert "09:00" in conflicts[0]


def test_get_todays_schedule_excludes_past_dates():
    """get_todays_schedule() only returns tasks due today, not past/future dates."""
    owner = Owner(name="Alex")
    buddy = Pet(name="Buddy", species="dog")
    owner.add_pet(buddy)

    today = date.today()
    yesterday = today - timedelta(days=1)

    buddy.add_task(Task(description="Today's walk",     time="09:00", due_date=today))
    buddy.add_task(Task(description="Yesterday's walk", time="09:00", due_date=yesterday))

    scheduler = Scheduler(owner)
    todays_tasks = scheduler.get_todays_schedule()

    assert len(todays_tasks) == 1
    assert todays_tasks[0]["description"] == "Today's walk"

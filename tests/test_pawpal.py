"""
tests/test_pawpal.py — Automated test suite for PawPal+
Run with: python -m pytest
"""

from datetime import date, timedelta
import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_pet():
    """A pet with no tasks."""
    return Pet(name="Mochi", species="dog", age=3)


@pytest.fixture
def sample_owner(sample_pet):
    """An owner with one pet."""
    owner = Owner(name="Jordan")
    owner.add_pet(sample_pet)
    return owner


# ── Task Tests ───────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """Verify that mark_complete() sets is_complete to True."""
    task = Task(description="Morning walk", time="08:00")
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True


def test_is_recurring_daily():
    """Daily tasks should be recognized as recurring."""
    task = Task(description="Feeding", time="07:00", frequency="daily")
    assert task.is_recurring() is True


def test_is_recurring_once():
    """One-time tasks should not be recurring."""
    task = Task(description="Vet visit", time="10:00", frequency="once")
    assert task.is_recurring() is False


# ── Pet Tests ────────────────────────────────────────────────────────────────

def test_add_task_increases_count(sample_pet):
    """Adding a task should increase the pet's task count."""
    initial_count = len(sample_pet.tasks)
    sample_pet.add_task(Task(description="Walk", time="08:00"))
    assert len(sample_pet.tasks) == initial_count + 1


def test_get_pending_tasks(sample_pet):
    """get_pending_tasks() should only return incomplete tasks."""
    t1 = Task(description="Walk", time="08:00")
    t2 = Task(description="Feed", time="09:00")
    t2.mark_complete()
    sample_pet.add_task(t1)
    sample_pet.add_task(t2)
    pending = sample_pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].description == "Walk"


# ── Scheduler Tests ──────────────────────────────────────────────────────────

def test_sort_by_time(sample_owner, sample_pet):
    """Tasks should be returned in chronological order."""
    sample_pet.add_task(Task(description="Afternoon walk", time="15:00"))
    sample_pet.add_task(Task(description="Morning walk",   time="08:00"))
    sample_pet.add_task(Task(description="Breakfast",      time="07:30"))

    scheduler = Scheduler(sample_owner)
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times)


def test_detect_conflicts(sample_owner, sample_pet):
    """Scheduler should flag two tasks at the same time for the same pet."""
    sample_pet.add_task(Task(description="Medication", time="09:00"))
    sample_pet.add_task(Task(description="Bath time",  time="09:00"))

    scheduler = Scheduler(sample_owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "09:00" in conflicts[0]


def test_no_conflicts(sample_owner, sample_pet):
    """Scheduler should return no warnings when times don't overlap."""
    sample_pet.add_task(Task(description="Walk",  time="08:00"))
    sample_pet.add_task(Task(description="Feed",  time="09:00"))

    scheduler = Scheduler(sample_owner)
    assert scheduler.detect_conflicts() == []


def test_recurring_task_creates_next_occurrence(sample_owner, sample_pet):
    """Marking a daily task complete should create a new task for the next day."""
    today = date.today()
    task = Task(description="Morning walk", time="08:00", frequency="daily", due_date=today)
    sample_pet.add_task(task)

    scheduler = Scheduler(sample_owner)
    task.mark_complete()
    scheduler.handle_recurring(task, sample_pet)

    new_task = sample_pet.tasks[-1]
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.is_complete is False
    assert new_task.description == "Morning walk"


def test_filter_by_status(sample_owner, sample_pet):
    """filter_by_status() should correctly separate complete and pending tasks."""
    t1 = Task(description="Walk", time="08:00")
    t2 = Task(description="Feed", time="09:00")
    t2.mark_complete()
    sample_pet.add_task(t1)
    sample_pet.add_task(t2)

    scheduler = Scheduler(sample_owner)
    assert len(scheduler.filter_by_status(complete=False)) == 1
    assert len(scheduler.filter_by_status(complete=True)) == 1
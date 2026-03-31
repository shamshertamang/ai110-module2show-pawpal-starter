from datetime import date, timedelta

from pawpal_system import Owner, Pet, Priority, Schedule, Task


# ---------------------------------------------------------------------------
# Existing basic tests
# ---------------------------------------------------------------------------

def test_mark_complete():
    task = Task(task_id=1, task_name="Walking", is_completed=False, duration=30, time=8, priority=Priority.HIGH, pet_id=1)
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_to_pet():
    pet = Pet(pet_id=1, name="Buddy", owner_id=1, species="Dog")
    assert len(pet.tasks) == 0
    task = Task(task_id=1, task_name="Feeding", is_completed=False, duration=10, time=9, priority=Priority.HIGH, pet_id=1)
    pet.tasks.append(task)
    assert len(pet.tasks) == 1


# ===========================================================================
# Behavior 1 — Recurring Task Generation  (docs/README.md §1)
# ===========================================================================

class TestRecurrenceLogic:
    """Confirm that marking a daily/weekly task complete creates the correct
    next-occurrence task, and non-recurring tasks return None."""

    def test_daily_recurrence_creates_next_day_task(self):
        """Happy path: daily task produces a new task with due_date + 1 day."""
        today = date(2026, 3, 31)
        task = Task(
            task_id=1, task_name="Morning Walk", is_completed=False,
            duration=30, time=8, priority=Priority.HIGH, pet_id=1,
            recurrence="daily", due_date=today,
        )
        next_task = task.mark_complete()

        assert task.is_completed is True
        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)
        assert next_task.is_completed is False
        assert next_task.task_id == 1001
        assert next_task.recurrence == "daily"

    def test_weekly_recurrence_creates_next_week_task(self):
        """Happy path: weekly task shifts due_date by 7 days."""
        today = date(2026, 3, 31)
        task = Task(
            task_id=5, task_name="Grooming", is_completed=False,
            duration=60, time=10, priority=Priority.MEDIUM, pet_id=1,
            recurrence="weekly", due_date=today,
        )
        next_task = task.mark_complete()

        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=7)

    def test_non_recurring_returns_none(self):
        """Edge case: non-recurring task returns None on completion."""
        task = Task(
            task_id=2, task_name="Vet Visit", is_completed=False,
            duration=60, time=14, priority=Priority.HIGH, pet_id=1,
            recurrence=None, due_date=date(2026, 4, 1),
        )
        assert task.mark_complete() is None

    def test_recurring_with_no_due_date_falls_back_to_today(self):
        """Edge case: due_date=None falls back to date.today()."""
        task = Task(
            task_id=3, task_name="Evening Feed", is_completed=False,
            duration=10, time=18, priority=Priority.LOW, pet_id=1,
            recurrence="daily", due_date=None,
        )
        next_task = task.mark_complete()
        assert next_task.due_date == date.today() + timedelta(days=1)

    def test_pet_complete_task_appends_next_occurrence(self):
        """Happy path: Pet.complete_task appends the new recurring task."""
        pet = Pet(pet_id=1, name="Buddy", owner_id=1, species="Dog")
        task = Task(
            task_id=10, task_name="Feed", is_completed=False,
            duration=10, time=9, priority=Priority.HIGH, pet_id=1,
            recurrence="daily", due_date=date(2026, 3, 31),
        )
        pet.tasks.append(task)
        next_task = pet.complete_task(task)

        assert next_task is not None
        assert len(pet.tasks) == 2
        assert pet.tasks[-1] is next_task


# ===========================================================================
# Behavior 2 — Sorting Correctness  (docs/README.md §2)
# ===========================================================================

class TestSortingCorrectness:
    """Verify tasks are returned sorted by priority, preference, then time."""

    def _make_task(self, tid, name, time, priority, duration=15):
        return Task(
            task_id=tid, task_name=name, is_completed=False,
            duration=duration, time=time, priority=priority, pet_id=1,
        )

    def test_sorted_by_priority(self):
        """Happy path: HIGH tasks appear before MEDIUM before LOW."""
        low = self._make_task(1, "Low Task", 8, Priority.LOW)
        high = self._make_task(2, "High Task", 10, Priority.HIGH)
        med = self._make_task(3, "Med Task", 9, Priority.MEDIUM)

        sched = Schedule().generate_schedule([low, high, med], available_time=120)
        names = [t.task_name for t in sched.get_tasks()]
        assert names == ["High Task", "Med Task", "Low Task"]

    def test_preferred_tasks_break_ties(self):
        """Happy path: among same-priority tasks, preferred names come first."""
        a = self._make_task(1, "Bath", 10, Priority.MEDIUM)
        b = self._make_task(2, "Nails", 11, Priority.MEDIUM)

        sched = Schedule().generate_schedule(
            [a, b], available_time=120, preferred_tasks=["Nails"],
        )
        names = [t.task_name for t in sched.get_tasks()]
        assert names == ["Nails", "Bath"]

    def test_time_breaks_remaining_ties(self):
        """Happy path: same priority & preference — earlier time comes first."""
        early = self._make_task(1, "Early", 7, Priority.HIGH)
        late = self._make_task(2, "Late", 15, Priority.HIGH)

        sched = Schedule().generate_schedule([late, early], available_time=120)
        names = [t.task_name for t in sched.get_tasks()]
        assert names == ["Early", "Late"]

    def test_empty_task_list(self):
        """Edge case: empty list produces empty schedule."""
        sched = Schedule().generate_schedule([], available_time=60)
        assert sched.get_tasks() == []
        assert sched.total_time == 0

    def test_all_tasks_exceed_available_time(self):
        """Edge case: every task is too large — nothing scheduled."""
        big = self._make_task(1, "Big", 8, Priority.HIGH, duration=120)
        sched = Schedule().generate_schedule([big], available_time=30)
        assert sched.get_tasks() == []
        assert sched.total_time == 0


# ===========================================================================
# Behavior 3 — Conflict Detection  (docs/README.md §3)
# ===========================================================================

class TestConflictDetection:
    """Verify that the scheduler flags tasks sharing the same time slot."""

    def _make_task(self, tid, name, time, priority=Priority.HIGH, duration=15):
        return Task(
            task_id=tid, task_name=name, is_completed=False,
            duration=duration, time=time, priority=priority, pet_id=1,
        )

    def test_duplicate_times_produce_warning(self):
        """Happy path: two tasks at the same hour trigger a conflict warning."""
        t1 = self._make_task(1, "Walk", 9)
        t2 = self._make_task(2, "Feed", 9)

        sched = Schedule().generate_schedule([t1, t2], available_time=120)
        explanation = sched.get_explanation()
        assert "Conflict warnings" in explanation
        assert "Walk" in explanation and "Feed" in explanation

    def test_no_conflicts_when_times_differ(self):
        """Edge case: distinct time slots produce no warnings."""
        t1 = self._make_task(1, "Walk", 8)
        t2 = self._make_task(2, "Feed", 10)

        sched = Schedule().generate_schedule([t1, t2], available_time=120)
        assert "Conflict warnings" not in sched.get_explanation()

    def test_no_warnings_on_empty_schedule(self):
        """Edge case: no tasks means no conflicts."""
        sched = Schedule().generate_schedule([], available_time=60)
        assert "Conflict warnings" not in sched.get_explanation()


# ===========================================================================
# Behavior 4 — Task Filtering  (docs/README.md §4)
# ===========================================================================

class TestTaskFiltering:
    """Verify Owner.filter_tasks by pet name and completion status."""

    def _setup_owner(self):
        owner = Owner(owner_id=1, name="Alice", email="a@b.com", phone_number="555", available_time=120)
        buddy = Pet(pet_id=1, name="Buddy", owner_id=1, species="Dog")
        luna = Pet(pet_id=2, name="Luna", owner_id=1, species="Cat")

        buddy.tasks = [
            Task(1, "Walk Buddy", False, 30, 8, Priority.HIGH, 1),
            Task(2, "Feed Buddy", True, 10, 9, Priority.MEDIUM, 1),
        ]
        luna.tasks = [
            Task(3, "Feed Luna", False, 10, 9, Priority.HIGH, 2),
        ]
        owner.add_current_pet(buddy)
        owner.add_current_pet(luna)
        return owner

    def test_filter_by_pet_name_and_incomplete(self):
        """Happy path: filter by pet name + completed=False."""
        owner = self._setup_owner()
        result = owner.filter_tasks(pet_name="Buddy", completed=False)
        assert len(result) == 1
        assert result[0].task_name == "Walk Buddy"

    def test_filter_completed_across_all_pets(self):
        """Happy path: completed=True across all pets."""
        owner = self._setup_owner()
        result = owner.filter_tasks(completed=True)
        assert len(result) == 1
        assert result[0].task_name == "Feed Buddy"

    def test_nonexistent_pet_returns_empty(self):
        """Edge case: pet name that matches nothing returns []."""
        owner = self._setup_owner()
        assert owner.filter_tasks(pet_name="Ghost") == []

    def test_no_filters_returns_all(self):
        """Edge case: no arguments returns every task."""
        owner = self._setup_owner()
        assert len(owner.filter_tasks()) == 3

    def test_owner_with_no_pets(self):
        """Edge case: owner with no current pets returns []."""
        owner = Owner(owner_id=2, name="Bob", email="b@b.com", phone_number="555", available_time=60)
        assert owner.filter_tasks() == []


# ===========================================================================
# Behavior 5 — Completed Tasks Skipped in Scheduling  (docs/README.md §5)
# ===========================================================================

class TestCompletedTasksSkipped:
    """Verify that already-completed tasks are excluded from scheduling."""

    def test_completed_tasks_excluded(self):
        """Happy path: completed task not in schedule, incomplete one is."""
        done = Task(1, "Done Task", True, 15, 8, Priority.HIGH, 1)
        todo = Task(2, "Todo Task", False, 15, 9, Priority.HIGH, 1)

        sched = Schedule().generate_schedule([done, todo], available_time=60)
        names = [t.task_name for t in sched.get_tasks()]
        assert "Todo Task" in names
        assert "Done Task" not in names

    def test_explanation_mentions_skipped(self):
        """Happy path: explanation notes the completed task was skipped."""
        done = Task(1, "Done Task", True, 15, 8, Priority.HIGH, 1)

        sched = Schedule().generate_schedule([done], available_time=60)
        assert "already completed" in sched.get_explanation()

    def test_all_completed_yields_empty_schedule(self):
        """Edge case: all tasks completed — schedule empty, total_time 0."""
        t1 = Task(1, "A", True, 15, 8, Priority.HIGH, 1)
        t2 = Task(2, "B", True, 20, 9, Priority.MEDIUM, 1)

        sched = Schedule().generate_schedule([t1, t2], available_time=120)
        assert sched.get_tasks() == []
        assert sched.total_time == 0

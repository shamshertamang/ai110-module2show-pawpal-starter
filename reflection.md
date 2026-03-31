# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design includes four classes: Owner, Pet, Task, and Schedule.

- **Owner** represents the pet owner and stores their contact info, available time for daily pet care, and lists of current and favorite pets. It provides methods to manage pets and update contact details.
- **Pet** represents an individual pet with a species and dietary preferences, linked to its owner.
- **Task** represents a single pet care activity (e.g., walking, feeding, grooming) with a duration, time, priority level (HIGH, MEDIUM, LOW), and completion status.
- **Schedule** holds a priority-sorted list of tasks and a total time tracker. Its core responsibility is generating a daily plan via `generate_schedule()`, which takes a list of tasks and the owner's available time, then produces an optimized schedule that fits within the time constraint.

The relationships are: an Owner owns many Pets (1-to-many), a Pet has many Tasks (1-to-many), an Owner has one Schedule (1-to-1), and a Schedule contains many Tasks (1-to-many).


**b. Design changes**

The design changed in three ways after comparing the UML diagram against the README requirements:

1. **Added `explanation` to Schedule** — The README requires the app to explain why it chose a particular plan. The original design had no way to capture this reasoning, so we added an `explanation` attribute and a `get_explanation()` method to `Schedule` so the scheduler can describe its decisions to the user.

2. **Added `edit_task()` to Task** — The README says users should be able to add *and edit* tasks, but the original design only supported marking tasks complete. We added an `edit_task()` method so users can update a task's name, duration, time, and priority after creation.

3. **Added `preferred_tasks` to Owner and `generate_schedule()`** — The README lists "owner preferences" as a scheduling constraint, but the original design only considered time and priority. We added a `preferred_tasks` list to `Owner` (e.g., "walking", "enrichment") and passed it into `generate_schedule()` so preferred task types are used as a tiebreaker when tasks share the same priority level.

4. **Added `tasks` list to Pet** — The UML shows a 1-to-many relationship between Pet and Task (`Pet "1" --o "*" Task`), but the original skeleton only stored a `pet_id` back-reference on Task with no way to navigate from Pet to its Tasks. We added a `tasks: list[Task]` attribute to `Pet` so the scheduler can collect all tasks by iterating through the owner's pets, making the relationship navigable from both sides.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints, applied in this order:

1. **Priority** (HIGH > MEDIUM > LOW) — the primary sort key. High-priority tasks like medication or feeding are scheduled first because missing them has the biggest impact on pet health.
2. **Owner preferences** — a tiebreaker within the same priority level. If two tasks are both HIGH priority, the one matching the owner's `preferred_tasks` list comes first.
3. **Time of day** — the final tiebreaker. Within the same priority and preference tier, earlier tasks (lower `time` value) are scheduled first so the plan follows a natural morning-to-evening flow.

Priority was ranked highest because a pet care app must ensure critical tasks (meds, feeding) always make the cut before optional ones (enrichment, grooming) when time is limited.

**b. Tradeoffs**

The conflict detector only checks for **exact time-slot matches** (two tasks at the same hour) rather than checking whether task durations actually overlap. For example, a 45-minute walk at 8:00 and a 10-minute feeding at 8:30 would not be flagged, even though they overlap by 15 minutes.

This tradeoff is reasonable because PawPal+ models time as a simple hour integer (`time=8` means "8:00"), not as a precise start/end window. Implementing true duration-based overlap detection would require changing `Task.time` from an hour to a minute-level timestamp and adding an end-time calculation — added complexity that isn't justified for a daily pet care planner where tasks are approximate and flexible. The exact-match approach catches the most common conflict (two tasks carelessly assigned to the same hour) while keeping the code simple and the data model lightweight.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
Design of the classes and their brainstorming, making plantUML, install VSCode extensions, refactoring code to make it cleaner and more readable.

- What kinds of prompts or questions were most helpful?
I gave locally focused prompts with whole file context by using @file or # codebase which helped me a lot easily.

**b. Judgment and verification**

when I had to update the main.py after making changes to the scheduling algorithm, the AI proposed massive changes to the file, I rejected it and told it to focus on simpler changes on incremental steps so I could verify each incremental steps.

To make sure that it was correct, I went through the code myself and checked if it was correct as per the system design and the desired result.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested 5 core behaviors across 23 pytest tests:

1. **Recurrence logic** (5 tests) — verified that completing a daily task creates a new task with `due_date + 1 day`, weekly shifts by 7 days, non-recurring returns `None`, and that `due_date=None` falls back to `date.today()`. Also confirmed `Pet.complete_task()` appends the new occurrence to the pet's task list.

2. **Sorting correctness** (5 tests) — confirmed the schedule sorts tasks by priority (HIGH > MEDIUM > LOW), then preferred task names as a tiebreaker, then by time of day. Also tested empty task lists and cases where all tasks exceed available time.

3. **Conflict detection** (3 tests) — verified that two tasks at the same time slot produce a warning in the explanation, no overlapping times returns no warnings, and an empty schedule produces no false positives.

4. **Task filtering** (5 tests) — tested `Owner.filter_tasks()` by pet name, completion status, and both combined. Covered edge cases like a nonexistent pet name returning `[]` and an owner with no pets.

5. **Completed tasks skipped** (3 tests) — confirmed that completed tasks are excluded from the generated schedule, the explanation mentions they were skipped, and an all-completed input yields an empty schedule with `total_time = 0`.

These tests were important because they validate the core scheduling contract: that the right tasks appear in the right order, conflicts are flagged, recurring tasks regenerate correctly, and filtering works as expected. Without them, a subtle sorting bug or a missed recurrence could silently produce bad daily plans for a pet owner.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

**Confidence: 4 out of 5 stars.** All 23 tests pass across both happy paths and edge cases for every core behavior. The scheduler correctly sorts, filters, skips completed tasks, detects same-hour conflicts, and generates recurring tasks.

The one star withheld reflects two gaps I would test next with more time:

- **Duration-based overlap** — the conflict detector only flags exact hour matches. A 45-minute task at 8:00 and a 10-minute task at 8:30 would not be flagged even though they overlap. Testing this would require changing the time model from hours to minutes.
- **Streamlit UI integration** — all tests currently exercise the backend classes directly. I would add end-to-end tests (using `streamlit.testing` or similar) to verify that button clicks, dropdown selections, and session state behave correctly in the actual app.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the scheduling algorithm and its transparency. The three-level sort (priority, preference, time) with a greedy fit is simple but effective, and the explanation log makes every decision visible — what was added, what was skipped, and why. The conflict detection on top of that gives pet owners actionable warnings instead of silent failures. The fact that 23 tests cover all of this and pass cleanly gives me real confidence in the system's reliability.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would redesign the time model. Currently `Task.time` is a simple hour integer (e.g., `8` for 8:00 AM), which limits conflict detection to exact-hour matches and makes it impossible to detect duration-based overlaps. Switching to minute-level timestamps with explicit start/end times would enable true overlap detection and allow more precise daily plans. I would also add the ability to edit and delete tasks from the Streamlit UI, and add `due_date` filtering so the owner can view tasks for a specific day rather than just all tasks at once.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is to design incrementally and verify at each step rather than building everything at once. Starting with UML gave me a clear map, but the design needed to evolve — adding `explanation`, `preferred_tasks`, `recurrence`, and `filter_tasks` only became obvious once I started implementing and testing. AI tools were most helpful when I gave them focused, file-scoped prompts and rejected overly ambitious suggestions in favor of small, verifiable changes. The combination of upfront design + incremental implementation + test-driven verification produced a system I actually trust.

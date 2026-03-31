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
Design brainstorming, making plantUML, install VSCode extensions
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

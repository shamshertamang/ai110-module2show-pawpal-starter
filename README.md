# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ goes beyond basic task lists with several scheduling enhancements:

- **Three-level priority sorting** — tasks are ordered by priority (HIGH > MEDIUM > LOW), then by owner preference (preferred task names win ties), then by time of day (morning-first).
- **Completed task filtering** — already-finished tasks are automatically skipped during scheduling so they don't consume available time.
- **Task filtering by pet or status** — `Owner.filter_tasks()` lets you narrow tasks by pet name, completion status, or both.
- **Conflict detection** — the scheduler warns when two tasks are assigned to the same time slot, surfaced in the schedule explanation rather than crashing.
- **Recurring tasks** — tasks marked as `"daily"` or `"weekly"` automatically spawn a new instance with an updated `due_date` when completed, using Python's `timedelta`.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Jordan
----------------------------------------
07:30 AM  Luna     Walk       (HIGH)
12:00 PM  Milo     Grooming   (LOW)
06:00 PM  Luna     Feeding    (MEDIUM)
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
python -m pytest
========================== test session starts ==========================
platform darwin -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/hajramuzammal/module 2/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 16 items                                                      

tests/test_pawpal.py ................                             [100%]

========================== 16 passed in 0.02s ===========================
(.venv) (base) hajramuzammal@Hajras-MacBook-Air ai110-module2show-pawpal-starter % python -m pytest
================= test session starts ==================
platform darwin -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/hajramuzammal/module 2/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 16 items                                     

tests/test_pawpal.py ................            [100%]

================== 16 passed in 0.02s ==================

Description:
Ran the full test suite (16 tests) covering task filtering, sorting by time, and recurring task generation, including edge cases like empty task lists, ties on identical times, and idempotency across repeated calls. All 16 tests passed.
Confidence Level: ⭐⭐⭐⭐☆ (4/5)
Core scheduling logic is well-tested, but conflict detection and priority sorting don't have dedicated tests yet, so I'm holding back one star until those are covered too.
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()` | Orders tasks by priority level (high to low) so the most urgent care tasks appear first in the daily plan. |
| Filtering | `Scheduler.get_todays_tasks()` | Filters the full task list down to only tasks due today across all pets. `Pet.get_upcoming_tasks()` is stubbed but not yet implemented. |
| Conflict handling | `Scheduler.check_conflicts()`, `Scheduler.detect_conflicts()` | `check_conflicts()` runs an O(n) check when a single task is added, comparing it against existing tasks. `detect_conflicts()` runs a sweep-line pass (O(n log n)) to generate a full conflict report across all tasks at once. |
| Recurring tasks | `Task.is_recurring`, `Task.recurrence_interval` | Recurring tasks are flagged with these attributes (e.g. daily/weekly), but `Scheduler.handle_recurrence()` — which would generate the next occurrence when a recurring task is completed — is currently a stub and not yet implemented. |

## 📸 Demo Walkthrough

1. **Enter your name as the owner.** On launch, the app asks for the owner's name (defaults to "Jordan"). This creates an `Owner` object that persists across the session.
2. **Add a pet.** Enter a pet's name, species, and age, then click "Add pet." The pet is attached to the owner and appears in a table of current pets below the form.
3. **Schedule a task for that pet.** Select the pet, enter a task type (e.g. "Morning walk"), a time, a duration in minutes, and a priority level (low/medium/high), then click "Add task." The task is attached to the selected pet via `Scheduler.add_task()`. If the new task's time overlaps with an existing task, a conflict warning appears automatically.
4. **Review all scheduled tasks.** Every task added so far — across all pets — appears in a table showing the pet, task type, time, duration, and priority.
5. **Generate today's schedule.** Click "Generate schedule" to see only the tasks due today, sorted earliest to latest, in a clean daily-plan table showing time, pet, task type, and priority.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

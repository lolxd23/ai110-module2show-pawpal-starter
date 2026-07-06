# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design consists of four classes: Owner, Pet, Task, and Scheduler. An Owner has a one-to-many relationship with Pet (one owner can have multiple pets), and each Pet has a one-to-many relationship with Task (one pet can have multiple tasks — feedings, walks, medications, appointments). The Scheduler class is not owned by any single entity; instead it operates across all Task objects system-wide, handling sorting, conflict detection, and recurrence logic. This keeps the data-holding classes (Owner, Pet, Task) separate from the algorithmic logic (Scheduler).
- What classes did you include, and what responsibilities did you assign to each?
Owner is responsible for representing the pet's caretaker — it holds the owner's name and their list of pets, and handles adding new pets and gathering all tasks across every pet they own.
Pet is responsible for representing an individual animal — it holds the pet's name, species, and age along with its list of tasks, and handles adding new tasks to itself and returning its own upcoming tasks.
Task is responsible for representing a single care event (a feeding, walk, medication, or appointment) — it holds the task type, time, recurrence info, priority, and completion status, and handles marking itself complete, checking if it's due today, and checking for conflicts with other tasks.
Scheduler is responsible for the algorithmic logic that spans the whole system — it doesn't hold pet-specific data itself, but instead sorts tasks by priority, detects scheduling conflicts, manages recurring tasks, and generates the "today's tasks" view across all owners and pets.

**b. Design changes**
- Did your design change during implementation?
Yes, my design changed after reviewing the AI's feedback on my initial skeleton. One significant change was adding a back-reference from Task to its owning Pet, along with a duration_mins attribute.gap and let the Scheduler's logic work as intended.
- If yes, describe at least one change and why you made it.
In my original design, Task only stored a time: datetime with no link back to which pet it belonged to and no sense of how long it lasted. This worked fine for a single flat list of tasks, but it broke down in two places: Scheduler.detect_conflicts() and get_todays_tasks() returned bare Task objects with no way to say "this is Luna's walk," which the UI needs to display; and conflicts_with() could only check for exact-time collisions since it had no duration to compare against, making real overlap detection (e.g., a 30-minute walk clashing with a vet visit starting 15 minutes later) impossible.
I made this change because without it, two of my core algorithmic features — conflict detection and generating a readable "today's tasks" view — couldn't actually be implemented correctly. Adding pet and duration_mins to Task closed that 
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
One tradeoff in my scheduler is around conflict detection. I currently have two separate methods that both check for task overlaps: check_conflicts(), which runs in O(n) and is used whenever a single task is added, and detect_conflicts(), which uses a sweep-line approach running in O(n log n) to generate a full conflict report across all tasks. Both methods implement essentially the same "does task A overlap task B" logic, just through different traversal strategies — which works fine individually, but makes the file harder to scan since the same core logic is duplicated in two places.
When I asked my AI coding assistant how this could be simplified for readability, it suggested having detect_conflicts() just call check_conflicts() for each task and dedupe the resulting pairs, collapsing the logic into a single code path. I considered this, but decided against fully adopting it: it would trade away the sweep-line's early-break optimization, dropping full system-wide conflict reports back to O(n²) instead of O(n log n). For a single owner managing a handful of pets, this performance difference is negligible in practice — task counts will stay small — so the readability gain probably outweighs the performance cost. This is the kind of tradeoff I'm still weighing: keep two clean, purpose-built traversals, or accept a slightly less optimal but more unified/readable implementation.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI throughout the full lifecycle of this project — not just for writing code, but for design review, implementation, and debugging. In the design phase, I used AI to help brainstorm and sketch the initial UML relationships between Owner, Pet, Task, and Scheduler, then had it generate the Python class skeleton (using dataclasses for Task and Pet) once the design was settled. Later, I gave AI my completed skeleton and asked it to review it for missing relationships and logic bottlenecks — this surfaced real gaps I hadn't caught, like the missing `pet` back-reference on `Task` and the lack of a `duration_mins` field, both of which were blocking correct conflict detection. I also used AI heavily for debugging: when my test suite failed with `AssertionError: assert None == []`, AI helped me trace it down to two unimplemented stub methods, and when a fix I thought I'd applied still wasn't taking effect, AI helped me systematically check whether I was actually running the file I thought I was (which turned out to be exactly the issue — a stale copy of `pawpal_system.py` was being imported instead of my edited one).

The most helpful prompts were ones where I gave AI my actual code and asked it to check it against something concrete — "review this skeleton for missing relationships" or "here's my failing test output, why is this happening" — rather than vague requests like "help me build a scheduler." Attaching real files and real error output got far more useful, specific answers than describing the problem abstractly.

**b. Judgment and verification**

One clear moment I didn't accept an AI suggestion as-is was around simplifying my conflict-detection logic. I have two methods — `check_conflicts()` (an O(n) check run when a single task is added) and `detect_conflicts()` (an O(n log n) sweep-line pass for a full system report) — that both implement similar overlap logic through different traversal strategies. When I asked AI how this could be simplified for readability, it suggested collapsing `detect_conflicts()` into a wrapper that just calls `check_conflicts()` per task. I considered this, but decided against it: doing so would trade away the sweep-line's early-break optimization, dropping full system-wide reports from O(n log n) back to O(n²). Since task counts for a single owner's pets will stay small, I judged the performance cost to be negligible, but I still weighed it deliberately rather than just taking the "cleaner" version at face value.

I verified AI's suggestions primarily through my test suite — for example, after AI implemented `handle_recurrence()`, I didn't just trust that it worked; I ran the actual pytest suite against it and traced every failure back to root cause (in one case, discovering the issue was environmental — a stale cached file — not a logic bug at all, which taught me not to assume every test failure means the code is wrong).

---

## 4. Testing and Verification

**a. What you tested**

I tested the core scheduling behaviors in `pawpal_system.py`: filtering a pet's incomplete tasks and sorting them by time (including edge cases like an empty task list, tasks with identical times needing stable insertion-order preservation, and making sure one pet's tasks don't leak into another pet's list), and the recurring-task logic in `handle_recurrence()` — generating correct next occurrences for daily and weekly intervals, correctly rolling a date over a month boundary, assigning unique task IDs when multiple recurring tasks are due at once, remaining idempotent so repeated calls don't duplicate follow-up tasks, and gracefully skipping a task if its owning pet no longer exists in the system.

These tests mattered because they covered the exact places where the logic was easy to get subtly wrong: date arithmetic across month boundaries, mutation during iteration, and idempotency are all classic sources of silent bugs that a quick manual check wouldn't catch.

**b. Confidence**

I'm confident (about 4 out of 5 stars) that the parts of the scheduler I tested — filtering, sorting by time, and recurrence — work correctly, since all 16 tests pass and they cover meaningful edge cases rather than just happy-path behavior. I'm less confident about `check_conflicts()`, `detect_conflicts()`, and `sort_by_priority()`, since none of those currently have dedicated tests. If I had more time, I'd test: overlapping tasks that share an exact boundary (task A ends exactly when task B starts — should that count as a conflict?), conflict detection across multiple pets versus within a single pet, priority sorting stability when multiple tasks share the same priority level, and what happens when `duration_mins` is zero or negative.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how the recurrence logic turned out, specifically the idempotency handling. It would have been easy to write `handle_recurrence()` in a way that silently generated duplicate follow-up tasks every time it ran, and catching that required thinking carefully about state (flipping `is_recurring` to `False` after generating a follow-up) rather than just making the happy path work.

**b. What you would improve**

If I had another iteration, I'd finish wiring the backend's full feature set into the Streamlit UI — right now `app.py` calls `get_todays_tasks()` for the schedule view, but doesn't expose `sort_by_priority()`, `detect_conflicts()`, or `complete_task()`/`handle_recurrence()` through any UI element, even though all of that logic exists and is tested in `pawpal_system.py`. I'd also add dedicated tests for conflict detection and priority sorting, since those are currently the least-verified parts of the system.

**c. Key takeaway**

One important thing I learned is that AI-assisted debugging is only as good as your ability to verify the environment you're actually running in — I spent a real chunk of time believing a fix hadn't worked, when the actual problem was that Python was importing a stale, un-updated copy of the file. AI could point me toward the right diagnostic commands, but confirming *which* file was actually executing required me to check it directly rather than just re-reading the code and assuming it was correct.
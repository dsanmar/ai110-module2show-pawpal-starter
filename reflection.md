# PawPal+ Project Reflection

## 0. System Design — Core User Actions

Three core actions the system must support:
1. **Add a pet** — an Owner registers a new Pet (name + species) to their household
2. **Schedule a task** — a Pet is assigned a Task with a description, time, frequency, and due date
3. **View today's schedule** — the Scheduler collects all tasks due today, sorts them by time, and surfaces any conflicts

---

## 1. System Design

**a. Initial design**

The system is built around four classes:

- **Task** (dataclass) — the atomic unit of pet care work. Holds `description`, `time` (HH:MM), `frequency` (once/daily/weekly), `is_complete`, and `due_date`. Responsible for its own recurrence logic via `mark_complete()`.
- **Pet** (dataclass) — aggregates Tasks for one animal. Responsible for owning and exposing its task list. Holds `name`, `species`, and a `tasks` list.
- **Owner** (dataclass) — aggregates Pets for a household. Provides a cross-pet flat view of all tasks via `get_all_tasks()`. Holds `name` and a `pets` list.
- **Scheduler** (service class) — pure-behavior class that wraps an Owner and provides scheduling operations: filtering by today's date, sorting by time, conflict detection, and recurrence handling. Does not own any data — it reads from Owner.

**b. Design changes**

Two meaningful changes emerged during implementation:

1. **`get_all_tasks()` returns dicts, not Task objects.** The initial design had Owner returning raw Task objects. During implementation it became clear that Streamlit's `st.table` needs dict/record format, and the "Mark Complete" button needs `pet_index` and `task_index` to navigate back to the mutable object in session state. Adding those indices to a dict was cleaner than adding them as attributes on Task.

2. **`mark_complete()` has a mixed return type (`Task | None`).** For `"once"` tasks it mutates in place and returns `None`; for recurring tasks it returns a new Task and leaves `self` unchanged. This was not explicit in the initial skeleton but fell naturally out of the recurrence semantics: recurring tasks should keep a history record, not overwrite themselves.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:
- **Time** (`HH:MM`) — the primary scheduling axis; tasks are sorted chronologically and conflicts are detected when two tasks share the same time slot.
- **Frequency** (`once` / `daily` / `weekly`) — determines recurrence; after a task is marked complete, recurring tasks automatically generate a successor with the next due date.
- **Due date** — determines which tasks appear in today's view; tasks with a past or future `due_date` are excluded from `get_todays_schedule()`.

Time was treated as the most important constraint because it is the most actionable signal for a daily care routine. Priority was deliberately excluded to keep the system simple and non-prescriptive — the owner decides which conflicts to resolve.

**b. Tradeoffs**

The conflict detection system warns but does not block. When two tasks share the same `HH:MM` time slot, the scheduler surfaces a warning string but still includes both tasks in the schedule. The owner decides whether to reschedule one.

This is reasonable because: (1) blocking task creation would be frustrating when the owner knows they can handle both tasks with help; (2) it keeps the system non-prescriptive — the scheduler is an advisor, not an enforcer. The tradeoff is that the conflict list can grow noisy if the owner adds many overlapping tasks without resolving them.

Additionally, conflict detection only checks **exact time matches** — it does not detect overlapping durations (e.g., a 30-minute task starting at 09:00 overlapping a task at 09:15). This is a deliberate simplification; duration is not stored in the Task dataclass.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used as the primary "lead architect" across all six phases: generating the initial UML, producing class skeletons with docstrings, implementing full logic, writing pytest tests, and wiring the Streamlit UI. The most useful prompts were **specific and structured** — listing exact field names, return types, and behavioral contracts (e.g., "for 'daily' tasks return a new Task with due_date+1 and reset is_complete to False"). Vague prompts produced vague output; detailed specs produced tight, correct implementations.

The most valuable AI feature was the ability to reason through the full Streamlit integration constraint — specifically recognizing that `pet_index`/`task_index` must be embedded in schedule dicts to allow the "Mark Complete" button to mutate the right object in session state.

**b. Judgment and verification**

The AI's initial sketch of `mark_complete()` for recurring tasks mutated `self.is_complete = True` (same as the "once" path) and then set `self.due_date += timedelta(days=1)`. This was incorrect: it would mark the current task complete AND reschedule it on the same object, losing the distinction between "this occurrence is done" and "here is the next occurrence." The corrected version creates a brand-new Task for the successor, leaving the original unchanged (the original's `is_complete` stays False to preserve history). This was verified by the `test_mark_complete_daily_returns_new_task` test, which explicitly asserts that `task.is_complete is False` after `mark_complete()` is called on a daily task.

---

## 4. Testing and Verification

**a. What you tested**

Six behaviors were tested:
1. `mark_complete()` on a "once" task — verifies the simplest completion path
2. `mark_complete()` on a "daily" task — verifies the recurrence logic and that the original is unchanged
3. Adding a task increases pet task count — basic data integrity
4. `sort_by_time()` returns chronological order — verifies the core sorting contract
5. `detect_conflicts()` catches two tasks at the same time — verifies conflict detection
6. `get_todays_schedule()` excludes past dates — verifies the date filter

These tests were important because they cover the four scheduling features (sort, filter, conflict, recurrence) and the two most dangerous mutation paths (`mark_complete` for once vs. recurring).

**b. Confidence**

**★★★★☆** — High confidence in the happy paths. The scheduler correctly sorts, detects conflicts, and handles recurrence for all three frequency types. Lower confidence in edge cases: What happens if `mark_complete()` is called twice on a "once" task? What if time strings are malformed (e.g., "9:00" vs "09:00")? What if a pet has no tasks? These are the next tests to write.

---

## 5. Reflection

**a. What went well**

The most satisfying part was the Streamlit integration. Solving the "Mark Complete" button problem — embedding `pet_index` and `task_index` in every schedule dict so the button can navigate back to the mutable object — was a clean, non-obvious design decision that made the UI feel fluid without hacks. The test suite also passed on the first run (6/6), validating the design choices made upfront.

**b. What you would improve**

If given another iteration:
- **Store task duration** — currently absent. Duration would enable detecting overlapping windows (not just exact-time conflicts), which is a much more realistic conflict model.
- **Replace time strings with `datetime.time` objects** — relying on lexicographic string sort works for "HH:MM" but fails silently if a user enters "9:00" (single-digit hour). Parsing to `datetime.time` at task creation would catch bad input early.
- **Add a weekly recurring test** — only daily recurrence is tested; a `+7 days` test would complete the coverage.

**c. Key takeaway**

The biggest lesson: **the UI constraint should drive the data model, not just the domain.** The shift from returning `Task` objects to returning dicts-with-indices was entirely caused by Streamlit's need to display data and mutate backend objects from the same record. Starting from "how will the Mark Complete button know which task to update?" and working backwards produced a cleaner design than starting from the domain model alone.

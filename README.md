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

## Smarter Scheduling

PawPal+ implements four scheduling features beyond basic task storage:

- **Chronological sorting** — Tasks are sorted by their `HH:MM` time string (24-hour format). Lexicographic comparison works correctly for 24-hour times, so no datetime parsing is needed.
- **Conflict detection** — When two or more tasks share the same time slot, the scheduler produces a warning string identifying the conflict. Tasks are not blocked — the owner decides whether to reschedule.
- **Filter by pet or status** — `filter_tasks()` accepts an optional `pet_name` and/or `completed` flag to narrow the task list for display or analysis.
- **Recurring task auto-rescheduling** — After a `daily` or `weekly` task is marked complete, a successor Task is automatically created with the next due date (`+1 day` or `+7 days`). One-time (`once`) tasks simply toggle `is_complete`.

## Features

- Multi-pet household support — one Owner, many Pets
- Per-pet task management with add/view operations
- Daily schedule view filtered by today's due date
- Chronological sorting by HH:MM time
- Conflict detection for overlapping time slots
- Daily and weekly recurring tasks with auto-rescheduling
- Mark-complete UI with session-state persistence

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

### What each test covers

| Test | What it verifies |
|------|-----------------|
| `test_mark_complete_once` | `is_complete` becomes True; return value is None |
| `test_mark_complete_daily_returns_new_task` | New Task returned with `due_date + 1`; original unchanged |
| `test_add_task_increases_count` | Pet task list grows correctly |
| `test_sort_by_time_returns_chronological_order` | HH:MM sort produces correct chronological order |
| `test_detect_conflicts_catches_same_time` | Two tasks at "09:00" produce a conflict warning |
| `test_get_todays_schedule_excludes_past_dates` | Yesterday's tasks excluded; today's tasks included |

**Confidence: ★★★★☆** — Core scheduling logic (sort, conflict detect, recurrence) is fully covered. Edge cases like midnight date boundaries or malformed time strings are not tested.

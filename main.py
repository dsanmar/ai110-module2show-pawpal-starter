"""PawPal+ demo script — shows Alex's pet schedule for today."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main():
    # --- Set up owner and pets ---
    alex = Owner(name="Alex")

    buddy = Pet(name="Buddy", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")

    alex.add_pet(buddy)
    alex.add_pet(whiskers)

    # --- Add tasks (including a deliberate 09:00 conflict and one daily recurring) ---
    today = date.today()

    buddy.add_task(Task(description="Morning walk",   time="09:00", frequency="daily",  due_date=today))
    buddy.add_task(Task(description="Evening feeding", time="18:00", frequency="daily",  due_date=today))
    whiskers.add_task(Task(description="Morning feeding", time="09:00", frequency="once",  due_date=today))
    whiskers.add_task(Task(description="Grooming",        time="14:00", frequency="weekly", due_date=today))
    whiskers.add_task(Task(description="Vet check-up",    time="11:00", frequency="once",   due_date=today))

    # --- Build schedule ---
    scheduler = Scheduler(alex)
    todays_tasks = scheduler.get_todays_schedule()
    sorted_tasks = scheduler.sort_by_time(todays_tasks)
    conflicts = scheduler.detect_conflicts(sorted_tasks)

    # --- Print schedule ---
    print(f"\n{'='*50}")
    print(f"  PawPal+ — Today's Schedule for {alex.name}")
    print(f"  Date: {today}")
    print(f"{'='*50}")

    if sorted_tasks:
        print(f"\n{'Time':<8} {'Pet':<12} {'Task':<22} {'Freq':<10}")
        print("-" * 56)
        for t in sorted_tasks:
            print(f"{t['time']:<8} {t['pet_name']:<12} {t['description']:<22} {t['frequency']:<10}")
    else:
        print("\n  No tasks scheduled for today.")

    # --- Print conflict warnings ---
    if conflicts:
        print(f"\n{'!'*50}")
        print("  SCHEDULING CONFLICTS DETECTED:")
        for warning in conflicts:
            print(f"  ⚠  {warning}")
        print(f"{'!'*50}")
    else:
        print("\n  No conflicts detected.")

    print()


if __name__ == "__main__":
    main()

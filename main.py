"""
main.py — CLI demo script for PawPal+
Run with: python main.py
"""

from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date

# --- Setup ---
owner = Owner(name="Jordan", email="jordan@email.com")

mochi = Pet(name="Mochi", species="dog", age=3)
whiskers = Pet(name="Whiskers", species="cat", age=5)

# --- Add tasks to Mochi ---
mochi.add_task(Task(description="Afternoon walk",  time="15:00", frequency="daily"))
mochi.add_task(Task(description="Morning walk",    time="08:00", frequency="daily"))
mochi.add_task(Task(description="Flea medication", time="09:00", frequency="weekly"))

# --- Add tasks to Whiskers ---
whiskers.add_task(Task(description="Breakfast",    time="07:30", frequency="daily"))
whiskers.add_task(Task(description="Vet checkup",  time="10:00", frequency="once"))
whiskers.add_task(Task(description="Playtime",     time="08:00", frequency="daily"))

# --- Add a conflict to demo conflict detection ---
mochi.add_task(Task(description="Bath time",       time="09:00", frequency="once"))

# --- Register pets with owner ---
owner.add_pet(mochi)
owner.add_pet(whiskers)

# --- Create scheduler ---
scheduler = Scheduler(owner)

# --- Print Today's Schedule (sorted) ---
print("=" * 45)
print(f"  🐾 PawPal+ — Today's Schedule for {owner.name}")
print("=" * 45)

for task in scheduler.sort_by_time():
    status = "✅" if task.is_complete else "🔲"
    repeat = f"[{task.frequency}]" if task.is_recurring() else "[once]"
    print(f"  {status} {task.time}  {task.description:<22} {repeat}")

# --- Conflict Detection ---
print("\n--- Conflict Check ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("No conflicts found!")

# --- Filter: pending tasks only ---
print("\n--- Pending Tasks ---")
for task in scheduler.filter_by_status(complete=False):
    print(f"  🔲 {task.time}  {task.description}")

# --- Test recurring task ---
print("\n--- Recurring Task Test ---")
morning_walk = mochi.tasks[1]  # "Morning walk"
print(f"Before: {morning_walk.description} | complete={morning_walk.is_complete} | due={morning_walk.due_date}")
morning_walk.mark_complete()
scheduler.handle_recurring(morning_walk, mochi)
print(f"After:  {morning_walk.description} | complete={morning_walk.is_complete}")
print(f"New task added: {mochi.tasks[-1].description} | due={mochi.tasks[-1].due_date}")

print("\n✅ Demo complete!")
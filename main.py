from pawpal_system import Owner, Pet, Task, Schedule, Priority

# Create owner with 60 minutes of available time
owner = Owner(owner_id=1, name="Mr. GitPro", email="gitpro@example.com", phone_number="555-1234", available_time=60)
owner.preferred_tasks = ["Walking", "Feeding"]

# Create two pets
buddy = Pet(pet_id=1, name="Buddy", owner_id=1, species="Dog", dietary_preferences=["grain-free"])
whiskers = Pet(pet_id=2, name="Whiskers", owner_id=1, species="Cat", dietary_preferences=["wet food"])

owner.add_current_pet(buddy)
owner.add_current_pet(whiskers)

# Create tasks OUT OF ORDER (mixed priorities, mixed times, one already completed)
# task2 and task4 are both at time=8 to trigger conflict detection
task1 = Task(task_id=1, task_name="Enrichment", is_completed=False, duration=15, time=14, priority=Priority.LOW, pet_id=2)
task2 = Task(task_id=2, task_name="Walking", is_completed=False, duration=30, time=8, priority=Priority.HIGH, pet_id=1)
task3 = Task(task_id=3, task_name="Grooming", is_completed=True, duration=20, time=10, priority=Priority.MEDIUM, pet_id=1)
task4 = Task(task_id=4, task_name="Feeding", is_completed=False, duration=10, time=8, priority=Priority.HIGH, pet_id=2)
task5 = Task(task_id=5, task_name="Vet Checkup", is_completed=False, duration=25, time=11, priority=Priority.MEDIUM, pet_id=1)

whiskers.tasks.append(task1)
buddy.tasks.append(task2)
buddy.tasks.append(task3)
whiskers.tasks.append(task4)
buddy.tasks.append(task5)

# --- Filtering demo ---
print("=" * 50)
print("  FILTERING DEMO")
print("=" * 50)

print("\nAll tasks:")
for t in owner.get_all_tasks():
    print(f"  {t.task_name:15s} | {t.priority.value:6s} | time={t.time:2d} | completed={t.is_completed}")

print("\nBuddy's tasks only:")
for t in owner.filter_tasks(pet_name="Buddy"):
    print(f"  {t.task_name:15s} | {t.priority.value:6s} | completed={t.is_completed}")

print("\nIncomplete tasks only:")
for t in owner.filter_tasks(completed=False):
    print(f"  {t.task_name:15s} | {t.priority.value:6s} | pet_id={t.pet_id}")

print("\nWhiskers' incomplete tasks:")
for t in owner.filter_tasks(pet_name="Whiskers", completed=False):
    print(f"  {t.task_name:15s} | {t.priority.value:6s}")

# --- Schedule demo (sorting + completed guard) ---
print("\n" + "=" * 50)
print("  SCHEDULE DEMO")
print("=" * 50)

all_tasks = owner.get_all_tasks()
schedule = Schedule()
schedule.generate_schedule(all_tasks, owner.available_time, owner.preferred_tasks)

print(f"\nSchedule for {owner.name} ({owner.available_time} min available):")
print("-" * 50)
for task in schedule.get_tasks():
    print(f"  [{task.priority.value:6s}] {task.task_name:15s} - {task.duration} min (time={task.time}:00)")
print("-" * 50)
print(f"  Total: {schedule.total_time} min / {owner.available_time} min")

print("\nExplanation:")
print(schedule.get_explanation())

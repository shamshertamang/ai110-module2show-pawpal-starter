from pawpal_system import Owner, Pet, Task, Schedule, Priority

# Create owner with 60 minutes of available time
owner = Owner(owner_id=1, name="Mr. GitPro", email="gitpro@example.com", phone_number="555-1234", available_time=60)
owner.preferred_tasks = ["Walking", "Feeding"]

# Create two pets
buddy = Pet(pet_id=1, name="Buddy", owner_id=1, species="Dog", dietary_preferences=["grain-free"])
whiskers = Pet(pet_id=2, name="Whiskers", owner_id=1, species="Cat", dietary_preferences=["wet food"])

owner.add_current_pet(buddy)
owner.add_current_pet(whiskers)

# Create tasks and assign to pets
task1 = Task(task_id=1, task_name="Walking", is_completed=False, duration=30, time=8, priority=Priority.HIGH, pet_id=1)
task2 = Task(task_id=2, task_name="Feeding", is_completed=False, duration=10, time=9, priority=Priority.HIGH, pet_id=2)
task3 = Task(task_id=3, task_name="Grooming", is_completed=False, duration=20, time=10, priority=Priority.MEDIUM, pet_id=1)
task4 = Task(task_id=4, task_name="Enrichment", is_completed=False, duration=15, time=11, priority=Priority.LOW, pet_id=2)

buddy.tasks.append(task1)
buddy.tasks.append(task3)
whiskers.tasks.append(task2)
whiskers.tasks.append(task4)

# Collect all tasks from owner's pets
all_tasks = []
for pet in owner.current_pets:
    all_tasks.extend(pet.tasks)

# Generate and display schedule
schedule = Schedule()
schedule.generate_schedule(all_tasks, owner.available_time, owner.preferred_tasks)

print("=" * 40)
print(f"  Today's Schedule for {owner.name}")
print("=" * 40)
for task in schedule.get_tasks():
    print(f"  [{task.priority.value}] {task.task_name} - {task.duration} min (Pet ID: {task.pet_id})")
print("-" * 40)
print(f"  Total time: {schedule.total_time} min / {owner.available_time} min available")
print()
print("Explanation:")
print(schedule.get_explanation())

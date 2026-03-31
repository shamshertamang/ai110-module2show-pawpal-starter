from pawpal_system import Pet, Task, Priority


def test_mark_complete():
    task = Task(task_id=1, task_name="Walking", is_completed=False, duration=30, time=8, priority=Priority.HIGH, pet_id=1)
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_to_pet():
    pet = Pet(pet_id=1, name="Buddy", owner_id=1, species="Dog")
    assert len(pet.tasks) == 0
    task = Task(task_id=1, task_name="Feeding", is_completed=False, duration=10, time=9, priority=Priority.HIGH, pet_id=1)
    pet.tasks.append(task)
    assert len(pet.tasks) == 1

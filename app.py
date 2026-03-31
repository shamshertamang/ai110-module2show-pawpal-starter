import streamlit as st
from pawpal_system import Owner, Pet, Task, Schedule, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize session state with a default Owner so data persists across reruns
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id=1, name="Jordan", email="", phone_number="", available_time=60
    )

st.title("🐾 PawPal+")

st.caption("A pet care planning assistant — add pets, create tasks, and generate an optimized daily schedule.")

st.divider()

owner = st.session_state.owner

# --- Owner Setup ---
st.subheader("Owner Info")
col_name, col_time = st.columns(2)
with col_name:
    owner_name = st.text_input("Owner name", value=owner.name)
with col_time:
    available_time = st.number_input(
        "Available time (minutes)", min_value=1, max_value=480, value=owner.available_time
    )
owner.name = owner_name
owner.available_time = available_time

# --- Add a Pet ---
st.subheader("Add a Pet")
col_pet, col_species = st.columns(2)
with col_pet:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["Dog", "Cat", "Other"])

if st.button("Add pet"):
    new_id = len(owner.current_pets) + 1
    pet = Pet(pet_id=new_id, name=pet_name, owner_id=owner.owner_id, species=species)
    owner.add_current_pet(pet)
    st.success(f"Added {pet_name} the {species}!")

if owner.current_pets:
    st.write("Current pets:")
    st.table([{"Name": p.name, "Species": p.species, "Tasks": len(p.tasks)} for p in owner.current_pets])
else:
    st.info("No pets yet. Add one above.")

# --- Add a Task ---
st.divider()
st.subheader("Add a Task")

if owner.current_pets:
    pet_options = {p.name: p for p in owner.current_pets}
    selected_pet_name = st.selectbox("Assign to pet", list(pet_options.keys()))

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"], index=0)

    if st.button("Add task"):
        selected_pet = pet_options[selected_pet_name]
        task_id = sum(len(p.tasks) for p in owner.current_pets) + 1
        task = Task(
            task_id=task_id,
            task_name=task_title,
            is_completed=False,
            duration=int(duration),
            time=0,
            priority=Priority[priority],
            pet_id=selected_pet.pet_id,
        )
        selected_pet.tasks.append(task)
        st.success(f"Added '{task_title}' for {selected_pet_name}!")

    # Show all tasks across pets
    all_tasks_display = []
    for p in owner.current_pets:
        for t in p.tasks:
            all_tasks_display.append(
                {"Pet": p.name, "Task": t.task_name, "Duration": t.duration, "Priority": t.priority.value}
            )
    if all_tasks_display:
        st.write("All tasks:")
        st.table(all_tasks_display)
else:
    st.info("Add a pet first, then you can create tasks for it.")

# --- Generate Schedule ---
st.divider()
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    all_tasks = []
    for p in owner.current_pets:
        all_tasks.extend(p.tasks)

    if not all_tasks:
        st.warning("No tasks to schedule. Add some tasks first.")
    else:
        schedule = Schedule()
        schedule.generate_schedule(all_tasks, owner.available_time, owner.preferred_tasks)

        st.markdown("### Today's Plan")
        for task in schedule.get_tasks():
            st.write(f"- **[{task.priority.value}]** {task.task_name} — {task.duration} min")
        st.write(f"**Total: {schedule.total_time} min / {owner.available_time} min available**")

        with st.expander("Scheduling explanation", expanded=True):
            st.text(schedule.get_explanation())

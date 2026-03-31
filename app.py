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
    st.table([
        {"Name": p.name, "Species": p.species, "Tasks": len(p.tasks),
         "Incomplete": sum(1 for t in p.tasks if not t.is_completed)}
        for p in owner.current_pets
    ])
else:
    st.info("No pets yet. Add one above.")

# --- Add a Task ---
st.divider()
st.subheader("Add a Task")

if owner.current_pets:
    pet_options = {p.name: p for p in owner.current_pets}
    selected_pet_name = st.selectbox("Assign to pet", list(pet_options.keys()))

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)

    col3, col4, col5 = st.columns(3)
    with col3:
        priority = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"], index=0)
    with col4:
        time_slot = st.number_input("Time slot (hour, 0–23)", min_value=0, max_value=23, value=8)
    with col5:
        recurrence = st.selectbox("Recurrence", ["None", "daily", "weekly"], index=0)

    if st.button("Add task"):
        selected_pet = pet_options[selected_pet_name]
        task_id = sum(len(p.tasks) for p in owner.current_pets) + 1
        task = Task(
            task_id=task_id,
            task_name=task_title,
            is_completed=False,
            duration=int(duration),
            time=int(time_slot),
            priority=Priority[priority],
            pet_id=selected_pet.pet_id,
            recurrence=None if recurrence == "None" else recurrence,
        )
        selected_pet.tasks.append(task)
        st.success(f"Added '{task_title}' for {selected_pet_name}!")

else:
    st.info("Add a pet first, then you can create tasks for it.")

# --- Filter & View Tasks ---
st.divider()
st.subheader("Tasks")

if owner.current_pets:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_pet = st.selectbox(
            "Filter by pet", ["All"] + [p.name for p in owner.current_pets], key="filter_pet"
        )
    with col_f2:
        filter_status = st.selectbox(
            "Filter by status", ["All", "Incomplete", "Completed"], key="filter_status"
        )

    pet_filter = None if filter_pet == "All" else filter_pet
    completed_filter = None if filter_status == "All" else (filter_status == "Completed")
    filtered = owner.filter_tasks(pet_name=pet_filter, completed=completed_filter)

    if filtered:
        # Build display rows with pet name lookup
        pet_by_id = {p.pet_id: p for p in owner.current_pets}
        task_rows = []
        for t in filtered:
            pet_obj = pet_by_id.get(t.pet_id)
            task_rows.append({
                "Pet": pet_obj.name if pet_obj else "?",
                "Task": t.task_name,
                "Time": f"{t.time}:00",
                "Duration": f"{t.duration} min",
                "Priority": t.priority.value,
                "Recurrence": t.recurrence or "—",
                "Status": "Done" if t.is_completed else "Todo",
            })
        st.table(task_rows)

        # --- Complete a Task ---
        incomplete = [t for t in filtered if not t.is_completed]
        if incomplete:
            task_to_complete = st.selectbox(
                "Mark a task complete",
                incomplete,
                format_func=lambda t: f"{t.task_name} ({t.priority.value})",
                key="complete_task",
            )
            if st.button("Complete task"):
                pet_obj = pet_by_id.get(task_to_complete.pet_id)
                if pet_obj:
                    next_task = pet_obj.complete_task(task_to_complete)
                    st.success(f"'{task_to_complete.task_name}' marked complete!")
                    if next_task:
                        st.info(
                            f"Recurring task: next '{next_task.task_name}' "
                            f"created for {next_task.due_date}"
                        )
                    st.rerun()
    else:
        st.info("No tasks match the current filters.")

# --- Preferred Tasks ---
st.divider()
st.subheader("Preferred Tasks")
preferred_input = st.text_input(
    "Task names the owner prefers (comma-separated)",
    value=", ".join(owner.preferred_tasks),
)
owner.preferred_tasks = [t.strip() for t in preferred_input.split(",") if t.strip()]

# --- Generate Schedule ---
st.divider()
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    all_tasks = owner.get_all_tasks()

    if not all_tasks:
        st.warning("No tasks to schedule. Add some tasks first.")
    else:
        schedule = Schedule()
        schedule.generate_schedule(all_tasks, owner.available_time, owner.preferred_tasks)

        scheduled = schedule.get_tasks()
        explanation = schedule.get_explanation()

        if not scheduled:
            st.warning("No tasks could fit in the available time.")
        else:
            st.markdown("### Today's Plan")

            # Display scheduled tasks as a sorted table
            pet_by_id = {p.pet_id: p for p in owner.current_pets}
            schedule_rows = []
            for i, task in enumerate(scheduled, 1):
                pet_obj = pet_by_id.get(task.pet_id)
                schedule_rows.append({
                    "#": i,
                    "Task": task.task_name,
                    "Pet": pet_obj.name if pet_obj else "?",
                    "Time": f"{task.time}:00",
                    "Duration": f"{task.duration} min",
                    "Priority": task.priority.value,
                })
            st.table(schedule_rows)

            # Time usage bar
            usage_pct = min(schedule.total_time / owner.available_time, 1.0)
            st.progress(usage_pct)
            st.write(f"**{schedule.total_time} min used / {owner.available_time} min available**")

        # Conflict warnings — shown prominently so the owner can act on them
        if "Conflict warnings" in explanation:
            conflict_section = explanation.split("Conflict warnings:\n")[-1]
            st.warning("**Schedule Conflicts Detected**")
            for line in conflict_section.strip().split("\n"):
                st.write(line.strip())
            st.caption(
                "These tasks overlap in the same time slot. "
                "Consider changing the time for one of them to avoid a scheduling conflict."
            )

        # Full explanation in a collapsible section
        with st.expander("Scheduling explanation"):
            st.text(explanation)

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+** — your pet care scheduling assistant.
Add your pets and tasks, then view today's optimized schedule.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

with st.expander("What you need to build", expanded=False):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

# --- Session state: single Owner object persists across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="My Household")

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Sidebar — manage pets
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Manage Pets")

    with st.form("add_pet_form", clear_on_submit=True):
        new_pet_name = st.text_input("Pet name", placeholder="e.g. Buddy")
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
        if st.form_submit_button("Add Pet"):
            if new_pet_name.strip():
                owner.add_pet(Pet(name=new_pet_name.strip(), species=new_species))
                st.success(f"Added {new_pet_name}!")
            else:
                st.error("Please enter a pet name.")

    if owner.pets:
        st.markdown("**Your pets:**")
        for pet in owner.pets:
            st.write(f"- {pet.name} ({pet.species})")
    else:
        st.info("No pets yet — add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Owner name (sync to session state without recreating Owner)
# ---------------------------------------------------------------------------
st.subheader("Owner Info")
owner_name_input = st.text_input("Owner name", value=owner.name)
if owner_name_input != owner.name:
    owner.name = owner_name_input

st.divider()

# ---------------------------------------------------------------------------
# Add a task to a selected pet
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

if owner.pets:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Select pet", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_description = st.text_input("Task description", value="Morning walk")
    with col2:
        task_time = st.text_input("Time (HH:MM)", value="09:00")
    with col3:
        task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        selected_pet_obj = next(p for p in owner.pets if p.name == selected_pet_name)
        selected_pet_obj.add_task(
            Task(description=task_description, time=task_time, frequency=task_frequency)
        )
        st.success(f"Added '{task_description}' to {selected_pet_name}.")
        st.rerun()

    # Show all current tasks across all pets
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**All tasks (across all pets):**")
        display_cols = ["pet_name", "description", "time", "frequency", "is_complete", "due_date"]
        st.table([{k: t[k] for k in display_cols} for t in all_tasks])
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet in the sidebar first, then you can schedule tasks.")

st.divider()

# ---------------------------------------------------------------------------
# Today's Schedule
# ---------------------------------------------------------------------------
st.subheader("Today's Schedule")
st.caption("Sorted chronologically. Conflicts are highlighted as warnings.")

if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("No pets found. Add a pet in the sidebar first.")
    else:
        scheduler = Scheduler(owner)
        todays_tasks = scheduler.get_todays_schedule()
        sorted_tasks = scheduler.sort_by_time(todays_tasks)
        conflicts = scheduler.detect_conflicts(sorted_tasks)

        for warning in conflicts:
            st.warning(f"⚠ {warning}")

        if sorted_tasks:
            for i, t in enumerate(sorted_tasks):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                col1.write(t["description"])
                col2.write(t["time"])
                col3.write(t["pet_name"])
                if col4.button("Done", key=f"complete_{i}"):
                    pet = owner.pets[t["pet_index"]]
                    task = pet.tasks[t["task_index"]]
                    successor = task.mark_complete()
                    if successor:
                        pet.add_task(successor)
                    st.rerun()
        else:
            st.info("No tasks scheduled for today. Add tasks with today's due date.")

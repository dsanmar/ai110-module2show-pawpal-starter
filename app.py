from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Custom CSS — warm pet-themed palette + paw print watermark
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ---- Page background with subtle paw watermark ---- */
    .stApp {
        background-color: #FFF8F0;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' opacity='0.06'%3E%3Cellipse cx='60' cy='75' rx='22' ry='18' fill='%23C07030'/%3E%3Cellipse cx='30' cy='48' rx='11' ry='14' fill='%23C07030'/%3E%3Cellipse cx='52' cy='36' rx='10' ry='13' fill='%23C07030'/%3E%3Cellipse cx='75' cy='36' rx='10' ry='13' fill='%23C07030'/%3E%3Cellipse cx='92' cy='50' rx='11' ry='14' fill='%23C07030'/%3E%3C/svg%3E");
        background-size: 160px 160px;
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {
        background-color: #FDF0E0;
        border-right: 2px solid #E8C99A;
    }

    /* ---- Main title ---- */
    h1 {
        color: #8B4513 !important;
        font-size: 2.6rem !important;
        letter-spacing: 1px;
    }

    /* ---- Subheadings ---- */
    h2, h3 {
        color: #A0522D !important;
    }

    /* ---- Section cards ---- */
    .section-card {
        background: #FFFFFF;
        border: 1.5px solid #E8C99A;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(160, 82, 45, 0.07);
    }

    /* ---- Task row card ---- */
    .task-row {
        background: #FFF3E8;
        border-left: 4px solid #D2691E;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
    }

    /* ---- Conflict row ---- */
    .conflict-row {
        background: #FFF0E0;
        border-left: 4px solid #E07030;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
    }

    /* ---- Primary buttons ---- */
    .stButton > button {
        background-color: #D2691E;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.4rem 1.2rem;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background-color: #A0522D;
        color: white;
    }

    /* ---- Form submit button (sidebar) ---- */
    [data-testid="stForm"] .stButton > button {
        background-color: #C07030;
        width: 100%;
    }

    /* ---- Info / success boxes ---- */
    .stAlert {
        border-radius: 10px;
    }

    /* ---- Dividers ---- */
    hr {
        border-color: #E8C99A;
    }

    /* ---- Tables ---- */
    table {
        border-radius: 10px;
        overflow: hidden;
    }
    thead tr th {
        background-color: #D2691E !important;
        color: white !important;
    }
    tbody tr:nth-child(even) {
        background-color: #FFF3E8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    "<h1>🐾 PawPal+</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#A0522D; font-size:1.05rem; margin-top:-0.5rem;'>"
    "Your pet care scheduling assistant — keep every paw on schedule.</p>",
    unsafe_allow_html=True,
)

# --- Session state ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="My Household")

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Sidebar — manage pets
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<h2 style='color:#8B4513; margin-bottom:0.2rem;'>🐶 Manage Pets</h2>",
        unsafe_allow_html=True,
    )
    st.caption("Add your furry family members here.")

    with st.form("add_pet_form", clear_on_submit=True):
        new_pet_name = st.text_input("Pet name", placeholder="e.g. Buddy")
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
        if st.form_submit_button("➕ Add Pet"):
            if new_pet_name.strip():
                owner.add_pet(Pet(name=new_pet_name.strip(), species=new_species))
                st.success(f"{new_pet_name} added!")
            else:
                st.error("Please enter a pet name.")

    st.divider()

    species_icons = {"dog": "🐕", "cat": "🐈", "other": "🐾"}
    if owner.pets:
        st.markdown("**Your pets:**")
        for pet in owner.pets:
            icon = species_icons.get(pet.species, "🐾")
            st.markdown(f"{icon} **{pet.name}** — *{pet.species}*")
    else:
        st.info("No pets yet — add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Owner Info
# ---------------------------------------------------------------------------
st.subheader("Owner Info")
owner_name_input = st.text_input("Owner name", value=owner.name)
if owner_name_input != owner.name:
    owner.name = owner_name_input

st.divider()

# ---------------------------------------------------------------------------
# Add a Task
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

    if st.button("➕ Add Task"):
        selected_pet_obj = next(p for p in owner.pets if p.name == selected_pet_name)
        selected_pet_obj.add_task(
            Task(description=task_description, time=task_time, frequency=task_frequency)
        )
        st.success(f"'{task_description}' added for {selected_pet_name}!")
        st.rerun()

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.markdown("**All tasks across all pets:**")
        display_cols = ["pet_name", "description", "time", "frequency", "is_complete", "due_date"]
        st.table([{k: t[k] for k in display_cols} for t in all_tasks])
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("🐾 Add a pet in the sidebar first, then schedule tasks here.")

st.divider()

# ---------------------------------------------------------------------------
# Today's Schedule
# ---------------------------------------------------------------------------
st.subheader("Today's Schedule")
st.caption("Tasks sorted chronologically. Conflicts flagged automatically.")

if st.button("Generate Schedule"):
    st.session_state.show_schedule = True

if st.session_state.get("show_schedule"):
    if not owner.pets:
        st.warning("No pets found. Add a pet in the sidebar first.")
    else:
        # Collect ALL of today's tasks including completed ones so greyed rows
        # remain visible after Done is clicked (st.rerun resets button state).
        today = date.today()
        all_today: list[dict] = []
        for pi, pet in enumerate(owner.pets):
            for ti, task in enumerate(pet.tasks):
                if task.due_date == today:
                    all_today.append({
                        "pet_name": pet.name,
                        "pet_index": pi,
                        "task_index": ti,
                        "description": task.description,
                        "time": task.time,
                        "frequency": task.frequency,
                        "is_complete": task.is_complete,
                        "due_date": task.due_date,
                    })

        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.sort_by_time(all_today)
        incomplete = [t for t in sorted_tasks if not t["is_complete"]]
        conflicts = scheduler.detect_conflicts(incomplete)

        for warning in conflicts:
            st.warning(f"⚠️ {warning}")

        if sorted_tasks:
            hcol1, hcol2, hcol3, hcol4 = st.columns([3, 1, 1, 1])
            hcol1.markdown("**Task**")
            hcol2.markdown("**Time**")
            hcol3.markdown("**Pet**")
            hcol4.markdown("**Done?**")
            st.divider()

            for i, t in enumerate(sorted_tasks):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                freq_badge = {"daily": "[daily]", "weekly": "[weekly]", "once": "[once]"}.get(t["frequency"], "")

                if t["is_complete"]:
                    col1.markdown(
                        f'<span style="color:grey; text-decoration:line-through;">{freq_badge} {t["description"]}</span>',
                        unsafe_allow_html=True,
                    )
                    col2.markdown(
                        f'<span style="color:grey;">{t["time"]}</span>',
                        unsafe_allow_html=True,
                    )
                    col3.markdown(
                        f'<span style="color:grey;">{t["pet_name"]}</span>',
                        unsafe_allow_html=True,
                    )
                    col4.button("✅", key=f"complete_{i}", disabled=True, help="Already done")
                else:
                    col1.markdown(f"{freq_badge} {t['description']}")
                    col2.markdown(f"`{t['time']}`")
                    col3.markdown(t["pet_name"])
                    if col4.button("✅", key=f"complete_{i}", help="Mark as done"):
                        pet = owner.pets[t["pet_index"]]
                        task = pet.tasks[t["task_index"]]
                        successor = task.mark_complete()
                        if successor:
                            pet.add_task(successor)
                        st.rerun()
        else:
            st.info("No tasks scheduled for today. Add tasks with today's due date.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    "<div style='text-align:center; color:#C07030; margin-top:2rem; font-size:0.85rem;'>"
    "🐾 PawPal+ &nbsp;|&nbsp; Built with Streamlit"
    "</div>",
    unsafe_allow_html=True,
)

import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+** — a smart pet care management system.
Add your pets, schedule their daily tasks, and let the scheduler organize everything for you.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

# ── Session State ─────────────────────────────────────────────────────────────
# Store Owner in session_state so it persists across Streamlit reruns

if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Owner + Pet Setup ─────────────────────────────────────────────────────────

st.subheader("Quick Demo Inputs")

owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Set Owner & Pet"):
    owner = Owner(name=owner_name)
    owner.add_pet(Pet(name=pet_name, species=species, age=1))
    st.session_state.owner = owner
    st.success(f"Created owner {owner_name} with pet {pet_name}!")

# ── Add Tasks ─────────────────────────────────────────────────────────────────

st.markdown("### Tasks")
st.caption("Add tasks below — these now feed directly into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_time = st.text_input("Time (HH:MM)", value="08:00")
with col3:
    task_freq = st.selectbox("Frequency", ["once", "daily", "weekly"])

if st.button("Add task"):
    if st.session_state.owner is None:
        st.warning("Please set your owner and pet first!")
    else:
        owner = st.session_state.owner
        pet = owner.pets[0]
        pet.add_task(Task(
            description=task_title,
            time=task_time,
            frequency=task_freq,
            due_date=date.today()
        ))
        st.success(f"Added '{task_title}' at {task_time}!")

# Show current tasks
if st.session_state.owner and st.session_state.owner.get_all_tasks():
    tasks = st.session_state.owner.get_all_tasks()
    st.write("Current tasks:")
    st.table([
        {
            "Task": t.description,
            "Time": t.time,
            "Frequency": t.frequency,
            "Status": "✅ Done" if t.is_complete else "🔲 Pending"
        }
        for t in tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Generate Schedule ─────────────────────────────────────────────────────────

st.subheader("Build Schedule")
st.caption("Generates a sorted schedule and checks for conflicts.")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please set your owner and pet first!")
    elif not st.session_state.owner.get_all_tasks():
        st.warning("Add some tasks first!")
    else:
        owner = st.session_state.owner
        scheduler = Scheduler(owner)

        # Conflict warnings
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No scheduling conflicts found!")

        # Sorted schedule
        st.markdown("### 📅 Today's Schedule (sorted by time)")
        sorted_tasks = scheduler.sort_by_time()
        st.table([
            {
                "Time": t.time,
                "Task": t.description,
                "Frequency": t.frequency,
                "Status": "✅ Done" if t.is_complete else "🔲 Pending"
            }
            for t in sorted_tasks
        ])

        # Mark complete
        pending = scheduler.filter_by_status(complete=False)
        if pending:
            st.markdown("### ✅ Mark a Task Complete")
            task_labels = [f"{t.time} — {t.description}" for t in pending]
            selected = st.selectbox("Select task", task_labels)
            if st.button("Mark Complete"):
                idx = task_labels.index(selected)
                task_to_complete = pending[idx]
                task_to_complete.mark_complete()
                pet = owner.pets[0]
                scheduler.handle_recurring(task_to_complete, pet)
                if task_to_complete.is_recurring():
                    st.success(f"Done! Next '{task_to_complete.description}' scheduled for tomorrow.")
                else:
                    st.success("Task marked complete!")
        else:
            st.success("All tasks are done for today! 🎉")

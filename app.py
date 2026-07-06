import streamlit as st

from datetime import date, datetime

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# Streamlit reruns this whole script on every interaction. Without this guard,
# a fresh (empty) Owner would replace the real one on every rerun. Checking
# "owner" not in st.session_state means we only construct it once, the first
# time the app loads, then reuse the same object out of the session "vault"
# on every rerun after that.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id=1, name=owner_name)

owner = st.session_state.owner
scheduler = Scheduler(owner)

st.divider()

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add pet"):
    # Owner.add_pet() is the Phase 2 method that owns this responsibility -
    # the UI's job is only to collect the form data and hand it off.
    new_pet = Pet(pet_id=len(owner.pets) + 1, name=pet_name, species=species, age=int(age))
    owner.add_pet(new_pet)
    st.success(f"Added {new_pet.name} ({new_pet.species}, age {new_pet.age}).")

if owner.pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species, "age": p.age} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Schedule a Task")

if not owner.pets:
    st.info("Add a pet before scheduling tasks.")
else:
    col1, col2 = st.columns(2)
    with col1:
        selected_pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
    with col2:
        task_type = st.text_input("Task type", value="Morning walk")

    col3, col4, col5 = st.columns(3)
    with col3:
        task_time = st.time_input("Time", value=datetime.now().time())
    with col4:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col5:
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        # Scheduler.add_task() is the Phase 2 method that owns this: it sets
        # task.pet_id and attaches the task to the chosen pet, so it's
        # immediately visible everywhere else that reads owner.get_all_tasks().
        selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        new_task = Task(
            task_id=len(owner.get_all_tasks()) + 1,
            task_type=task_type,
            time=datetime.combine(date.today(), task_time),
            duration_mins=int(duration),
            priority=Priority[priority_label.upper()],
        )
        conflict_warnings = scheduler.add_task(selected_pet, new_task)
        st.success(f"Added '{task_type}' for {selected_pet.name}.")
        for warning in conflict_warnings:
            st.warning(warning)

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": (owner.get_pet(t.pet_id) or Pet(0, "?", "?", 0)).name,
                "task_type": t.task_type,
                "time": t.time.strftime("%I:%M %p"),
                "duration_minutes": t.duration_mins,
                "priority": t.priority.name,
            }
            for t in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Shows today's tasks across all pets, earliest first.")

if st.button("Generate schedule"):
    # Scheduler.get_todays_tasks() is the Phase 2 method that owns this
    # filtering logic - the UI just displays whatever it returns.
    todays_tasks = sorted(scheduler.get_todays_tasks(), key=lambda t: t.time)

    if not todays_tasks:
        st.info("No tasks scheduled for today yet.")
    else:
        st.write("Today's Schedule:")
        st.table(
            [
                {
                    "time": t.time.strftime("%I:%M %p"),
                    "pet": (owner.get_pet(t.pet_id) or Pet(0, "?", "?", 0)).name,
                    "task_type": t.task_type,
                    "priority": t.priority.name,
                }
                for t in todays_tasks
            ]
        )

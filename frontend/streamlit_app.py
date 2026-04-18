import streamlit as st
import requests

API_URL = "http://localhost:5000"

# Page config
st.set_page_config(page_title="Task Tracker", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
.card {
    padding: 15px;
    border-radius: 10px;
    background-color: white;
    margin-bottom: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("📋 Task Tracker Dashboard")

# Sidebar
st.sidebar.title("Navigation")
option = st.sidebar.radio("Go to", ["Add Task", "View Tasks", "Progress"])

# ------------------ ADD TASK ------------------
if option == "Add Task":
    st.subheader("➕ Add New Task")

    task = st.text_input("Enter task")

    if st.button("Add Task"):
        if task:
            requests.post(f"{API_URL}/add-task", json={"title": task})
            st.success("Task added successfully!")
        else:
            st.warning("Please enter a task")

# ------------------ VIEW TASKS ------------------
elif option == "View Tasks":
    st.subheader("📌 All Tasks")

    if st.button("Refresh"):
        res = requests.get(f"{API_URL}/tasks")
        tasks = res.json()

        if tasks:
            for t in tasks:
                status = "✅ Completed" if t["completed"] else "⏳ Pending"

                st.markdown(f"""
                <div class="card">
                    <h4>{t['title']}</h4>
                    <p>Status: {status}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No tasks available")

    st.subheader("✔ Mark Task as Completed")

    task_id = st.number_input("Enter Task ID", min_value=1)

    if st.button("Complete Task"):
        res = requests.put(f"{API_URL}/complete-task/{task_id}")
        if res.status_code == 200:
            st.success("Task marked as completed!")
        else:
            st.error("Task not found")

# ------------------ PROGRESS ------------------
elif option == "Progress":
    st.subheader("📊 Task Progress")

    res = requests.get(f"{API_URL}/tasks")
    tasks = res.json()

    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])

    if total > 0:
        progress = completed / total
    else:
        progress = 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Tasks", total)
    col2.metric("Completed", completed)
    col3.metric("Pending", total - completed)

    st.progress(progress)

    st.write(f"Completion Rate: {progress*100:.2f}%")
import requests
import streamlit as st

API_URL = "http://localhost:5000"
PRIORITIES = ["High", "Medium", "Low"]

st.set_page_config(page_title="Task Tracker", page_icon="✅", layout="centered")
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
    }
    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
    }
    .app-hero {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1rem 1rem 0.9rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.4rem 0.6rem;
    }
    .task-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #6366f1;
        border-radius: 10px;
        padding: 0.7rem 0.8rem;
        margin-bottom: 0.4rem;
    }
    .task-meta {
        color: #475569;
        font-size: 0.86rem;
    }
    .priority-pill {
        display: inline-block;
        padding: 0.08rem 0.45rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .p-high { background: #fee2e2; color: #991b1b; }
    .p-medium { background: #fef3c7; color: #92400e; }
    .p-low { background: #dcfce7; color: #166534; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("✅ Task Tracker")
st.caption("Simple and clear task management")


def safe_get_tasks():
    try:
        response = requests.get(f"{API_URL}/tasks", timeout=5)
        if response.status_code == 200:
            return response.json(), None
        return [], "Could not fetch tasks from API."
    except requests.exceptions.RequestException:
        return [], "Backend is not reachable. Start API at http://localhost:5000."


def create_task(title, category, priority):
    payload = {
        "title": title,
        "category": category or "General",
        "priority": priority,
    }
    return requests.post(f"{API_URL}/add-task", json=payload, timeout=5)


def priority_badge(priority):
    level = (priority or "Medium").strip().lower()
    if level == "high":
        return '<span class="priority-pill p-high">High</span>'
    if level == "low":
        return '<span class="priority-pill p-low">Low</span>'
    return '<span class="priority-pill p-medium">Medium</span>'


tasks, error = safe_get_tasks()
if error:
    st.error(error)

total = len(tasks)
completed = len([task for task in tasks if task.get("completed")])
pending = total - completed

st.markdown('<div class="app-hero">', unsafe_allow_html=True)
st.markdown("### Your Daily Tasks")
st.caption("Track work clearly, finish faster.")
st.markdown("</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total", total)
    st.markdown("</div>", unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Pending", pending)
    st.markdown("</div>", unsafe_allow_html=True)
with c3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Completed", completed)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.subheader("Add New Task")
with st.form("add_task_form", clear_on_submit=True):
    task_title = st.text_input("Task title", placeholder="Example: Submit assignment")
    col_a, col_b = st.columns(2)
    task_category = col_a.text_input("Category", placeholder="General")
    task_priority = col_b.selectbox("Priority", PRIORITIES, index=1)
    add_clicked = st.form_submit_button("Add Task")

    if add_clicked:
        if not task_title.strip():
            st.warning("Please enter a task title.")
        else:
            try:
                response = create_task(task_title.strip(), task_category.strip(), task_priority)
                if response.status_code == 200:
                    st.success("Task added.")
                    st.rerun()
                else:
                    st.error("Failed to add task.")
            except requests.exceptions.RequestException:
                st.error("Could not connect to backend.")

st.divider()
st.subheader("Task List")

left, right = st.columns([2, 1])
search_text = left.text_input("Search", placeholder="Type part of task title")
status_filter = right.selectbox("Show", ["All", "Pending", "Completed"])

filtered_tasks = tasks
if search_text.strip():
    needle = search_text.strip().lower()
    filtered_tasks = [task for task in filtered_tasks if needle in task.get("title", "").lower()]

if status_filter != "All":
    expected = status_filter == "Completed"
    filtered_tasks = [task for task in filtered_tasks if task.get("completed") == expected]

if not filtered_tasks:
    st.info("No tasks found.")
else:
    for task in filtered_tasks:
        row1, row2, row3 = st.columns([5, 2, 2])

        status_text = "Completed" if task.get("completed") else "Pending"
        row1.markdown(
            f"""
            <div class="task-card">
                <div><strong>#{task['id']} {task.get('title', '')}</strong></div>
                <div class="task-meta">
                    Category: {task.get('category', 'General')} |
                    Priority: {priority_badge(task.get('priority', 'Medium'))} |
                    Status: {status_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        toggle_label = "Undo" if task.get("completed") else "Complete"
        if row2.button(toggle_label, key=f"toggle_{task['id']}", use_container_width=True):
            try:
                response = requests.put(f"{API_URL}/toggle-task/{task['id']}", timeout=5)
                if response.status_code == 200:
                    st.rerun()
                else:
                    st.error("Unable to update task.")
            except requests.exceptions.RequestException:
                st.error("Could not connect to backend.")

        if row3.button("Delete", key=f"delete_{task['id']}", use_container_width=True):
            try:
                response = requests.delete(f"{API_URL}/delete-task/{task['id']}", timeout=5)
                if response.status_code == 200:
                    st.rerun()
                else:
                    st.error("Unable to delete task.")
            except requests.exceptions.RequestException:
                st.error("Could not connect to backend.")

        st.divider()
import requests
import streamlit as st

API_URL = "http://localhost:5000"
PRIORITIES = ["High", "Medium", "Low"]

st.set_page_config(page_title="Task Tracker", page_icon="✅", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(120deg, #f8fbff 0%, #eef3fb 100%);
    }
    .hero {
        background: linear-gradient(120deg, #4f46e5, #0891b2);
        color: #fff;
        padding: 1.2rem 1.4rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(9, 31, 67, 0.18);
    }
    .task-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 0.85rem 0.9rem;
        margin-bottom: 0.7rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }
    .pill {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .pill-high { background: #fee2e2; color: #991b1b; }
    .pill-medium { background: #fef3c7; color: #92400e; }
    .pill-low { background: #dcfce7; color: #166534; }
    </style>
    """,
    unsafe_allow_html=True,
)


def safe_get_tasks():
    try:
        response = requests.get(f"{API_URL}/tasks", timeout=5)
        if response.status_code == 200:
            return response.json(), None
        return [], "Unable to fetch tasks from API."
    except requests.exceptions.RequestException:
        return [], "Backend is unreachable. Start Flask API at http://localhost:5000."


def priority_class(priority):
    normalized = (priority or "Medium").strip().lower()
    if normalized == "high":
        return "pill pill-high"
    if normalized == "low":
        return "pill pill-low"
    return "pill pill-medium"


st.markdown(
    """
    <div class="hero">
      <h2 style="margin:0;">Task Tracker Pro</h2>
      <p style="margin:0.3rem 0 0;">Organize smarter with priorities, filters, quick actions, and progress insights.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tasks, error = safe_get_tasks()
if error:
    st.error(error)

total_tasks = len(tasks)
completed_tasks = len([task for task in tasks if task.get("completed")])
pending_tasks = total_tasks - completed_tasks
completion_rate = (completed_tasks / total_tasks * 100) if total_tasks else 0.0

mc1, mc2, mc3, mc4 = st.columns(4)
mc1.metric("Total", total_tasks)
mc2.metric("Completed", completed_tasks)
mc3.metric("Pending", pending_tasks)
mc4.metric("Progress", f"{completion_rate:.0f}%")
st.progress(completion_rate / 100)

tab_manage, tab_board = st.tabs(["Manage Tasks", "Task Board"])

with tab_manage:
    st.subheader("Create Task")
    with st.form("create_task_form", clear_on_submit=True):
        title = st.text_input("Task title")
        category = st.text_input("Category", placeholder="General")
        priority = st.selectbox("Priority", PRIORITIES, index=1)
        submitted = st.form_submit_button("Add Task")

        if submitted:
            payload = {
                "title": title,
                "category": category or "General",
                "priority": priority,
            }
            try:
                response = requests.post(f"{API_URL}/add-task", json=payload, timeout=5)
                if response.status_code == 200:
                    st.success("Task added.")
                    st.rerun()
                else:
                    st.error("Failed to add task. Please check input.")
            except requests.exceptions.RequestException:
                st.error("Could not reach backend API.")

    st.subheader("Quick Actions")
    if not tasks:
        st.info("No tasks available yet.")
    else:
        action_col1, action_col2, action_col3 = st.columns([1, 1, 2])
        selected_task_id = action_col1.selectbox(
            "Task ID",
            [task["id"] for task in tasks],
            key="quick_task_select",
        )
        action_type = action_col2.selectbox("Action", ["Toggle Done", "Delete"])

        if action_col3.button("Apply Action", use_container_width=True):
            try:
                if action_type == "Delete":
                    response = requests.delete(f"{API_URL}/delete-task/{selected_task_id}", timeout=5)
                else:
                    response = requests.put(f"{API_URL}/toggle-task/{selected_task_id}", timeout=5)
                if response.status_code == 200:
                    st.success("Action completed.")
                    st.rerun()
                else:
                    st.error("Action failed. Task may not exist.")
            except requests.exceptions.RequestException:
                st.error("Could not reach backend API.")

with tab_board:
    st.subheader("Task Board")
    left, right = st.columns([2, 1])

    search = left.text_input("Search tasks", placeholder="Type keyword...")
    status_filter = right.selectbox("Status", ["All", "Pending", "Completed"])

    sort_by = st.selectbox("Sort by", ["Newest", "Priority (High to Low)", "A-Z"])

    filtered = tasks
    if search:
        filtered = [task for task in filtered if search.lower() in task.get("title", "").lower()]
    if status_filter != "All":
        expected = status_filter == "Completed"
        filtered = [task for task in filtered if task.get("completed") == expected]

    if sort_by == "Priority (High to Low)":
        order = {"High": 0, "Medium": 1, "Low": 2}
        filtered = sorted(filtered, key=lambda t: order.get(t.get("priority", "Medium"), 1))
    elif sort_by == "A-Z":
        filtered = sorted(filtered, key=lambda t: t.get("title", "").lower())
    else:
        filtered = sorted(filtered, key=lambda t: t.get("id", 0), reverse=True)

    if not filtered:
        st.info("No tasks match your filters.")
    else:
        for task in filtered:
            done_badge = "✅ Done" if task.get("completed") else "🕒 Pending"
            p_class = priority_class(task.get("priority"))
            st.markdown(
                f"""
                <div class="task-card">
                    <div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;">
                        <div>
                            <div style="font-weight:600;">#{task["id"]} - {task.get("title", "Untitled")}</div>
                            <div style="font-size:0.86rem;color:#475569;">
                                Category: {task.get("category", "General")} | {done_badge}
                            </div>
                        </div>
                        <div class="{p_class}">{task.get("priority", "Medium")}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
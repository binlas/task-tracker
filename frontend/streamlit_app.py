import streamlit as st
import requests

API_URL = "http://localhost:5000"

st.title("📋 Task Tracker Dashboard")

# Add Task
st.subheader("Add Task")
task_input = st.text_input("Enter task")

if st.button("Add Task"):
    if task_input:
        res = requests.post(f"{API_URL}/add-task", json={"title": task_input})
        st.success("Task Added!")

# View Tasks
st.subheader("All Tasks")

if st.button("Refresh Tasks"):
    res = requests.get(f"{API_URL}/tasks")
    tasks = res.json()

    for task in tasks:
        status = "✅" if task["completed"] else "❌"
        st.write(f"{task['id']}. {task['title']} {status}")

# Complete Task
st.subheader("Complete Task")
task_id = st.number_input("Enter Task ID", min_value=1, step=1)

if st.button("Mark Completed"):
    res = requests.put(f"{API_URL}/complete-task/{task_id}")
    if res.status_code == 200:
        st.success("Task Completed!")
    else:
        st.error("Task not found")
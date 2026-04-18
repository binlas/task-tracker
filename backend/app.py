from datetime import datetime

from flask import Flask, request, jsonify

app = Flask(__name__)
tasks = []

@app.route('/')
def home():
    return "Task Tracker API Running"

@app.route('/add-task', methods=['POST'])
def add_task():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return {"error": "Title is required"}, 400

    task = {
        "id": len(tasks) + 1,
        "title": title,
        "completed": False,
        "priority": data.get("priority", "Medium"),
        "category": data.get("category", "General"),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    tasks.append(task)
    return jsonify(task)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/complete-task/<int:task_id>', methods=['PUT'])
def complete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return jsonify(task)
    return {"error": "Not found"}, 404


@app.route('/toggle-task/<int:task_id>', methods=['PUT'])
def toggle_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            return jsonify(task)
    return {"error": "Not found"}, 404


@app.route('/delete-task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            deleted = tasks.pop(index)
            return jsonify(deleted)
    return {"error": "Not found"}, 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, request, jsonify

app = Flask(__name__)
tasks = []

@app.route('/')
def home():
    return "Task Tracker API Running"

@app.route('/add-task', methods=['POST'])
def add_task():
    data = request.get_json()
    task = {
        "id": len(tasks) + 1,
        "title": data['title'],
        "completed": False
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
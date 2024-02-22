from flask import Flask, request, jsonify
import sqlite3


app = Flask(__name__)


@app.route('/add_task/', methods=['POST'])
def add_task():
    data = request.get_json()
    description = data.get('description')
    due_date = data.get('due_date')

    with sqlite3.connect('task_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO tasks
                       (description, due_date, completed) VALUES (?, ?, ?)""",
                       (description, due_date, 0))

    return jsonify({"message": "Task added successfully"})


@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    with sqlite3.connect('task_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()

    return jsonify(tasks)


@app.route('/complete_task/<int:id>', methods=['PUT'])
def complete_task(id):
    with sqlite3.connect('task_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (id,))

    return jsonify({"message": "Task completed successfully"})


@app.route('/delete_task/<int:id>', methods=['DELETE'])
def delete_task(id):
    with sqlite3.connect('task_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))

    return jsonify({"message": "Task deleted successfully"})


if __name__ == "__main__":
    app.run(debug=True)

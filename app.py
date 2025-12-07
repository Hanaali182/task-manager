
from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
TASKS_FILE = "tasks.json"


# Load tasks from JSON file
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []


# Save tasks to JSON file
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f)


@app.route("/")
def index():
    tasks = load_tasks()
    total = len(tasks)
    completed = sum(1 for task in tasks if task.get("status") == "complete")
    return render_template("index.html", tasks=tasks, total=total, completed=completed)


@app.route("/add", methods=["POST"])
def add_task():
    tasks = load_tasks()
    title = request.form.get("title")
    priority = request.form.get("priority")
    due_date = request.form.get("due_date")
    if title:
        tasks.append(
            {
                "title": title,
                "priority": priority,
                "due_date": due_date,
                "status": "pending",
            }
        )
        save_tasks(tasks)
    return redirect(url_for("index"))


# NOTE: The <int:task_id> had been HTML-escaped; fixed here
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect(url_for("index"))


@app.route("/toggle/<int:task_id>")
def toggle_status(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks[task_id]["status"] = (
            "complete" if tasks[task_id]["status"] == "pending" else "pending"
        )
        save_tasks(tasks)
    return redirect(url_for("index"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    tasks = load_tasks()
    if request.method == "POST":
        tasks[task_id]["title"] = request.form.get("title")
        tasks[task_id]["priority"] = request.form.get("priority")
        tasks[task_id]["due_date"] = request.form.get("due_date")
        save_tasks(tasks)
        return redirect(url_for("index"))
    return render_template("edit.html", task=tasks[task_id], task_id=task_id)


# ---- NEW: clear all tasks route to match url_for('clear_tasks') in your template
@app.route("/clear", methods=["POST"], endpoint="clear_tasks")
def clear_tasks():
    # Replace tasks with an empty list
    save_tasks([])
    return redirect(url_for("index"))
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    # Run in debug for development convenience
    app.run(debug=True)

import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

TASK_FILE = "tasks.json"

def load_tasks():
    """Load tasks from JSON file."""
    if os.path.exists(TASK_FILE):
        try:
            with open(TASK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_tasks(tasks):
    """Save tasks to JSON file."""
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def next_task_id(tasks):
    """Generate next unique task ID."""
    return max([t.get('id', 0) for t in tasks], default=0) + 1

app = Flask(__name__)
tasks = load_tasks()

@app.route("/", methods=["GET", "POST"])
def home():
    """Main page: display tasks and handle new task submission."""
    global tasks
    
    if request.method == "POST":
        # Get form data
        title = request.form.get("title", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "")
        
        if title:
            new_task = {
                "id": next_task_id(tasks),
                "title": title,
                "priority": priority,
                "due_date": due_date,
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            tasks.append(new_task)
            save_tasks(tasks)
        
        return redirect(url_for("home"))
    
    # Sort tasks: incomplete first, then by priority
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    sorted_tasks = sorted(tasks, key=lambda t: (t.get("completed", False), priority_order.get(t.get("priority", "Medium"), 1)))
    
    return render_template("index.html", tasks=sorted_tasks, total=len(tasks), completed=sum(1 for t in tasks if t.get("completed")))

@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    """Mark a task as complete/pending."""
    global tasks
    for task in tasks:
        if task.get("id") == task_id:
            task["completed"] = not task.get("completed")
            break
    save_tasks(tasks)
    return redirect(url_for("home"))

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    """Delete a task."""
    global tasks
    tasks = [t for t in tasks if t.get("id") != task_id]
    save_tasks(tasks)
    return redirect(url_for("home"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    """Edit an existing task."""
    global tasks
    task = next((t for t in tasks if t.get("id") == task_id), None)
    
    if not task:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        task["title"] = request.form.get("title", "").strip() or task["title"]
        task["priority"] = request.form.get("priority", task.get("priority", "Medium"))
        task["due_date"] = request.form.get("due_date", "")
        save_tasks(tasks)
        return redirect(url_for("home"))
    
    return render_template("edit.html", task=task)

@app.route("/ping")
def ping():
    """Health check endpoint."""
    return "pong"

import socket
import webbrowser

def get_local_ip():
    """Detect local machine IP for LAN access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f" * Running on http://127.0.0.1:5000 (loopback)")
    print(f" * Running on http://{local_ip}:5000 (LAN)")
    app.run(debug=True, host="0.0.0.0", port=5000)

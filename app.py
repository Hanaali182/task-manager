
import os
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text

app = Flask(__name__)

# Homepage message (you can change this later for your CI/CD demo)
app.config["HOMEPAGE_MESSAGE"] = "Hello from Flask + DevOps CI/CD (v1)"

# Use DATABASE_URL from environment (Render will inject this)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tasks.db")

# Create DB engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=({"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
)

# -----------------------------
# Database setup
# -----------------------------
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            priority TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'pending'
        )
    """))

# -----------------------------
# Helpers
# -----------------------------
def fetch_all_tasks():
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, title, priority, due_date, status FROM tasks ORDER BY id ASC")).mappings().all()
        return [dict(row) for row in rows]

def add_task_db(title, priority=None, due_date=None):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO tasks (title, priority, due_date, status) VALUES (:title, :priority, :due_date, 'pending')"),
                     {"title": title, "priority": priority, "due_date": due_date})

def delete_task_db(task_id):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM tasks WHERE id = :id"), {"id": task_id})

def toggle_status_db(task_id):
    with engine.begin() as conn:
        row = conn.execute(text("SELECT status FROM tasks WHERE id = :id"), {"id": task_id}).fetchone()
        if row:
            new_status = "complete" if row[0] == "pending" else "pending"
            conn.execute(text("UPDATE tasks SET status = :status WHERE id = :id"), {"status": new_status, "id": task_id})

def get_task_db(task_id):
    with engine.begin() as conn:
        row = conn.execute(text("SELECT id, title, priority, due_date, status FROM tasks WHERE id = :id"), {"id": task_id}).mappings().fetchone()
        return dict(row) if row else None

def edit_task_db(task_id, title, priority=None, due_date=None):
    with engine.begin() as conn:
        conn.execute(text("UPDATE tasks SET title = :title, priority = :priority, due_date = :due_date WHERE id = :id"),
                     {"title": title, "priority": priority, "due_date": due_date, "id": task_id})

def clear_tasks_db():
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM tasks"))

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    tasks = fetch_all_tasks()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("status") == "complete")
    return render_template("index.html", tasks=tasks, total=total, completed=completed)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority") or None
    due_date = request.form.get("due_date") or None
    if title:
        add_task_db(title, priority, due_date)
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    delete_task_db(task_id)
    return redirect(url_for("index"))

@app.route("/toggle/<int:task_id>")
def toggle_status(task_id):
    toggle_status_db(task_id)
    return redirect(url_for("index"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    task = get_task_db(task_id)
    if not task:
        return redirect(url_for("index"))
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        priority = request.form.get("priority") or None
        due_date = request.form.get("due_date") or None
        if title:
            edit_task_db(task_id, title, priority, due_date)
        return redirect(url_for("index"))
    return render_template("edit.html", task=task, task_id=task_id)

@app.route("/clear", methods=["POST"], endpoint="clear_tasks")
def clear_tasks():
    clear_tasks_db()
    return redirect(url_for("index"))

# -----------------------------
# App start
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


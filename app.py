
import os
import ssl
from flask import Flask, render_template, request, redirect, url_for, abort
from sqlalchemy import create_engine, text

app = Flask(__name__)
app.config["HOMEPAGE_MESSAGE"] = "Hello from Flask + DevOps CI/CD (v1)"



# ---------- DB selection & DSN normalization ----------
USE_SQLITE = os.getenv("USE_SQLITE") == "1"

def normalize_dsn(dsn: str) -> str:
    """
    Normalize DSN for SQLAlchemy:
    - Postgres: force pg8000 driver ("postgresql+pg8000://")
    - SQLite stays as-is
    """
    if dsn.startswith("postgresql+pg8000://"):
        return dsn
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", "postgresql+pg8000://", 1)
    return dsn  # sqlite:///...

if USE_SQLITE:
    SQLALCHEMY_URL = "sqlite:///tasks.db"
else:
    RAW_DSN = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_URL = normalize_dsn(RAW_DSN)

# ---------- SSL context only for pg8000 ----------
def build_ssl_context():
    """
    Build an SSL context for pg8000 (Render requires TLS).
    """
    if not SQLALCHEMY_URL.startswith("postgresql+pg8000://"):
        return None
    ctx = ssl.create_default_context()
    ca_file = os.getenv("PG_CA_FILE")
    if ca_file and os.path.exists(ca_file):
        ctx.load_verify_locations(cafile=ca_file)
    return ctx

CONNECT_ARGS = {}
ssl_ctx = build_ssl_context()
if ssl_ctx:
    CONNECT_ARGS["ssl_context"] = ssl_ctx
    CONNECT_ARGS["timeout"] = int(os.getenv("PG_TIMEOUT", "15"))

engine = create_engine(
    SQLALCHEMY_URL,
    pool_pre_ping=True,
    connect_args=CONNECT_ARGS,
)



DB_READY = False
DB_ERROR = None

# ---------- Schema setup ----------
def ensure_schema():
    """
    Create schema if needed; dialect-aware for Postgres & SQLite.
    """
    global DB_READY, DB_ERROR
    try:
        dialect = engine.url.get_dialect().name
        if dialect == "postgresql":
            create_sql = """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    priority TEXT,
                    due_date TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """
        else:
            create_sql = """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    priority TEXT,
                    due_date TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """
        with engine.begin() as conn:
            conn.execute(text(create_sql))
        DB_READY = True
        DB_ERROR = None
    except Exception as e:
        DB_READY = False
        DB_ERROR = str(e)

ensure_schema()

# ---------- DB helpers ----------
def fetch_all_tasks():
    if not DB_READY:
        return []
    with engine.begin() as conn:
        rows = conn.execute(text(
            "SELECT id, title, priority, due_date, status FROM tasks ORDER BY id ASC"
        )).mappings().all()
        return [dict(row) for row in rows]

def add_task_db(title, priority=None, due_date=None):
    if not DB_READY:
        abort(503, f"Database not ready: {DB_ERROR}")
    with engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO tasks (title, priority, due_date, status) VALUES (:title, :priority, :due_date, 'pending')"
        ), {"title": title, "priority": priority, "due_date": due_date})

def delete_task_db(task_id):
    if not DB_READY:
        abort(503, f"Database not ready: {DB_ERROR}")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM tasks WHERE id = :id"), {"id": task_id})

def toggle_status_db(task_id):
    if not DB_READY:
        abort(503, f"Database not ready: {DB_ERROR}")
    with engine.begin() as conn:
        row = conn.execute(text("SELECT status FROM tasks WHERE id = :id"), {"id": task_id}).fetchone()
        if row:
            current = row[0] if not hasattr(row, "keys") else row["status"]
            new_status = "complete" if current == "pending" else "pending"
            conn.execute(text(
                "UPDATE tasks SET status = :status WHERE id = :id"
            ), {"status": new_status, "id": task_id})

def get_task_db(task_id):
    if not DB_READY:
        abort(503, f"Database not ready: {DB_ERROR}")
    with engine.begin() as conn:
        row = conn.execute(text(
            "SELECT id, title, priority, due_date, status FROM tasks WHERE id = :id"
        ), {"id": task_id}).mappings().fetchone()
        return dict(row) if row else None

def edit_task_db(task_id, title, priority=None, due_date=None):
    if not DB_READY:
        abort(503, f"Database not ready: {DB_ERROR}")
    with engine.begin() as conn:
        conn.execute(text(
            "UPDATE tasks SET title = :title, priority = :priority, due_date = :due_date WHERE id = :id"
        ), {"title": title, "priority": priority, "due_date": due_date, "id": task_id})

def clear_tasks_db():
    if not DB_READY:
        abort(503, f"Database not ready: {DB_ERROR}")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM tasks"))

# ---------- Routes ----------
@app.route("/")
def index():
    global DB_READY
    if not DB_READY:
        ensure_schema()
    if not DB_READY:
        return (f"<h1>{app.config['HOMEPAGE_MESSAGE']}</h1>"
                f"<p><strong>Database not ready.</strong></p>"
                f"<pre>{DB_ERROR}</pre>"), 503
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

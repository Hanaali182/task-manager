
# Task Manager

A feature-rich task management application built with **Flask**.

## ✅ Features
- ➕ Add, ✏️ Edit, and 🗑️ Delete tasks
- ✅ Mark tasks as **complete** or **pending**
- 🎯 Set task priority (**High**, **Medium**, **Low**)
- 📅 Add due dates to tasks
- 💾 Persistent storage using **JSON**
- 🖥️ Clean, responsive UI

---

## ⚙️ Setup & Run

### Requirements
- Python **3.7+**
- Windows PowerShell or Bash
- Flask (installed via `requirements.txt`)

---

### Quick Start (Clone & Run in 3 Commands)
```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/flask-task-manager.git
cd flask-task-manager

# 2. Create and activate virtual environment
python -m venv .venv && .\.venv\Scripts\Activate.ps1   # (Windows)
# OR
python3 -m venv .venv && source .venv/bin/activate     # (Linux/Mac)

# 3. Install dependencies and run
pip install -r requirements.txt
python app.py


## 🚀 Deployment Pipeline (Auto-Update)

This project is connected to **Render** for continuous deployment. Here’s how it works:

1. **Local Development**  
   Make changes in VS Code (e.g., edit `app.py`, templates, or CSS).

2. **Push to GitHub**  
   ```bash
   git add .
   git commit -m "Describe your change"
   git push


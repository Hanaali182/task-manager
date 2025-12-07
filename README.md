
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

### Installation (First Time Only)

#### Windows PowerShell
```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Allow script execution for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 3. Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt


# Inside your virtual environment
python app.py

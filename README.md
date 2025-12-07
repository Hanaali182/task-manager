# Task Manager

A feature-rich task management application built with Flask.

## Features
- Add, edit, and delete tasks
- Mark tasks as complete/pending
- Set task priority (High, Medium, Low)
- Add due dates to tasks
- Persistent storage (JSON)
- Clean, responsive UI

## Setup & Run

### Requirements
- Python 3.7+
- Windows PowerShell or bash

### Installation (first time only)

#### Windows PowerShell
\\\powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
\\\

#### macOS/Linux or Git Bash
\\\ash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
\\\

### Run the App

#### Windows PowerShell
\\\powershell
. .\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -u .\app.py
\\\

#### macOS/Linux or Git Bash
\\\ash
source .venv/bin/activate
python app.py
\\\

Then open your browser to:
- **Localhost**: http://127.0.0.1:5000/
- **LAN**: http://<your-machine-ip>:5000/

### Project Structure
\\\
task_manager/
├── app.py                 # Flask app & routes
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── templates/
│   ├── index.html         # Main UI
│   └── edit.html          # Edit task page
├── static/
│   └── style.css          # Styling
└── tasks.json             # Saved tasks (auto-created)
\\\

### Usage
1. Enter a task, priority, and due date
2. Click "Add Task"
3. View tasks in the list below
4. Click checkmark to mark complete
5. Click delete (🗑️) to remove
6. Click edit (✏️) to modify

### Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3
- **Data**: JSON (file-based)
- **Server**: Flask development server

# Task Management API — Local Setup & Usage

This is a small FastAPI-based task management backend I built for experimenting with tasks, subtasks, dependencies, analytics, and event logging.  
If you want to run it locally, the steps below should get everything running without issues.

---

## 🚀 Prerequisites

- Python **3.11+**
- PostgreSQL installed and running locally

---

## 📌 1. Create the Database

```bash
psql -U postgres -c "CREATE DATABASE tasks;"
```

---

## 📂 2. Clone the Repo & Create Virtual Env

```bash
git clone <repo_url> backend-task
cd backend-task
python3 -m venv .venv
source .venv/bin/activate
```

---

## 🔧 3. Create the `.env` File

Here's the exact `.env` I use locally:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tasks
SECRET_KEY=backendtasksecretkey
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 📦 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🏗️ 5. Create Database Tables

(No migrations for now.)

```bash
python create_tables.py
```

---

## ▶️ 6. Run the Server

```bash
uvicorn app.main:app --reload --port=8000
```

API docs:

👉 http://localhost:8000/docs

---

# 🧪 API Walkthrough (With Sample Commands)

Below are example curl commands you can run directly to test everything.

---

## 1️⃣ Register Admin User

```bash
curl -X POST "http://localhost:8000/auth/register" \
 -d "email=admin@example.com" \
 -d "password=secret123" \
 -d "full_name=Admin User"
```

---

## 2️⃣ Login as Admin

```bash
curl -X POST "http://localhost:8000/auth/login" \
 -d "email=admin@example.com" \
 -d "password=secret123"
```

Example response:

```json
{
  "access_token": "<TOKEN>",
  "token_type": "bearer"
}
```

Store the token:

```bash
export TOKEN=<TOKEN>
```

---

## 3️⃣ Create Another User

```bash
curl -X POST "http://localhost:8000/auth/register" \
 -d "email=john@example.com" \
 -d "password=pass123" \
 -d "full_name=John Doe"
```

---

## 4️⃣ Create a Task (tags + due date)

```bash
curl -X POST "http://localhost:8000/tasks/" \
 -H "Authorization: Bearer $TOKEN" \
 -d "title=Build API" \
 -d "description=Implement FastAPI backend" \
 -d "priority=1" \
 -d "tags=backend,urgent" \
 -d "due_date=2025-01-25T10:00:00"
```

Sample returned ID:

```
9597ac04-7793-4f66-bfd0-44052198e3e9
```

Save it:

```bash
export TASK1=<TASK_ID>
```

---

## 5️⃣ Create a Subtask

```bash
curl -X POST "http://localhost:8000/tasks/" \
 -H "Authorization: Bearer $TOKEN" \
 -d "title=Write CRUD operations" \
 -d "parent_id=$TASK1"
```

Sample returned ID:

```
04cc18eb-44d8-46be-8d04-b1d942846bb7
```

Save it:

```bash
export SUBTASK=<SUBTASK_ID>
```

---

## 6️⃣ Filter Tasks by Tag

```bash
curl -X GET "http://localhost:8000/tasks/?tag=backend" \
 -H "Authorization: Bearer $TOKEN"
```

Example output:

```json
[
  {
    "description": "Implement FastAPI backend",
    "priority": 1,
    "id": "9597ac04-7793-4f66-bfd0-44052198e3e9",
    "tags": "backend,urgent",
    "status": "todo",
    "title": "Build API"
  }
]
```

---

## 7️⃣ Add a Dependency

(Subtask depends on the main task)

```bash
curl -X POST "http://localhost:8000/tasks/$SUBTASK/depends-on/$TASK1" \
 -H "Authorization: Bearer $TOKEN"
```

---

## 8️⃣ Bulk Update Multiple Tasks

Example:

- Mark main task as `in_progress`
- Change subtask priority

```bash
curl -X POST "http://localhost:8000/tasks/bulk" \
 -H "Authorization: Bearer $TOKEN" \
 -H "Content-Type: application/json" \
 -d '[
   {"id": "'"$TASK1"'", "fields": {"status": "in_progress"}},
   {"id": "'"$SUBTASK"'", "fields": {"priority": 5}}
 ]'
```

---

## 9️⃣ Overdue Tasks Analytics

```bash
curl -X GET "http://localhost:8000/tasks/analytics/overdue" \
 -H "Authorization: Bearer $TOKEN"
```

---

## 🔟 Task Distribution Analytics

```bash
curl -X GET "http://localhost:8000/tasks/analytics/distribution" \
 -H "Authorization: Bearer $TOKEN"
```

Example:

```json
[
  { "status": "todo", "count": 1 },
  { "status": "in_progress", "count": 1 }
]
```

---

## 1️⃣1️⃣ Timeline Events for a Task

```bash
curl -X GET "http://localhost:8000/tasks/$TASK1/events?days=7" \
 -H "Authorization: Bearer $TOKEN"
```

Sample:

```json
[
  {
    "action": "created",
    "details": "Task created",
    "task_id": "9597ac04-7793-4f66-bfd0-44052198e3e9"
  }
]
```

---

## 1️⃣2️⃣ Get Full Task Details

```bash
curl -X GET "http://localhost:8000/tasks/$TASK1" \
 -H "Authorization: Bearer $TOKEN"
```

---

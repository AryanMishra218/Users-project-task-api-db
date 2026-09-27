# Users, Projects & Tasks API — with Database

Task 3 of the Innovation Hacks Full Stack Development Internship.
This builds directly on Task 2, replacing the in-memory Python
dictionaries with a **real, persistent database** using SQLAlchemy.

## What changed since Task 2

| Task 2 | Task 3 |
|---|---|
| `app/store.py` (Python dicts, wiped on every restart) | Real database tables (survive restarts) |
| No relationships, just matching IDs by hand | Real foreign keys + ORM relationships |
| Validation only in Python | Validation in Python **and** enforced by the database itself |

The route files (`app/routes/*.py`) barely changed — only *where the
data lives* changed. That's the benefit of keeping storage logic
separate from route logic.

## Tech Stack

- Python 3 + Flask
- **SQLAlchemy** (via Flask-SQLAlchemy) — works with SQLite, PostgreSQL, or MySQL using the *same code*
- **SQLite by default** (a single file, zero setup) — great for development
- **PostgreSQL-ready** — switch by changing one environment variable, no code changes

I tested this project against **both** SQLite and a real local
PostgreSQL server before handing it over, including confirming that
the database itself rejects invalid data (see "Schema-level validation" below).

## Database Schema & Relationships

```
User (1) ────< (many) Project      [Project.owner_id → User.id]
User (1) ────< (many) Task         [Task.assignee_id → User.id]
Project (1) ─< (many) Task         [Task.project_id  → Project.id]
```

- A **User** can own many **Projects** and be assigned many **Tasks**.
- A **Project** belongs to one owner and has many **Tasks**.
- A **Task** belongs to exactly one **Project**, and optionally has one **assignee** (User).
- Deleting a Project also deletes its Tasks (`cascade="all, delete-orphan"`) — no orphaned rows left behind.

### Schema-level validation (not just Python checks)

- `users.email` has a database `UNIQUE` constraint — a duplicate email is physically impossible to insert, not just blocked by our code.
- `projects.owner_id` and `tasks.project_id` / `tasks.assignee_id` are real foreign keys — the database refuses a value that doesn't point to an existing row.
- `tasks.status` and `tasks.priority` have `CheckConstraint`s restricting them to fixed sets of values (`todo`/`in-progress`/`done` and `low`/`medium`/`high`). I proved this by inserting bad data directly with raw SQL, bypassing Flask entirely — PostgreSQL rejected it with `violates check constraint "valid_status"`.

## Project Structure

```
users-projects-tasks-api-db/
├── app/
│   ├── __init__.py         # App factory — now also initializes the DB and creates tables
│   ├── config.py           # Reads SECRET_KEY and DATABASE_URL from environment
│   ├── extensions.py       # The shared `db = SQLAlchemy()` instance
│   ├── errors.py           # Custom ApiError for consistent error responses
│   ├── validators.py       # Reusable input validation functions
│   ├── models/
│   │   ├── user.py         # User model
│   │   ├── project.py      # Project model
│   │   └── task.py         # Task model (with CheckConstraints + @validates)
│   └── routes/
│       ├── users.py
│       ├── projects.py
│       └── tasks.py
├── run.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation & Running Locally (SQLite — recommended to start)

```bash
git clone <your-repo-url>
cd users-projects-tasks-api-db
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

That's it — no database installation needed. A file called `app.db`
appears in the project folder the first time you run it; that's your
entire database. **Stop the server (Ctrl+C) and start it again — your
data is still there.** That's the whole point of Task 3.

## Switching to PostgreSQL

1. Install PostgreSQL locally (or use a free hosted one like Neon or Supabase).
2. Create a database and user.
3. In your `.env`, set:
   ```
   DATABASE_URL=postgresql+psycopg2://youruser:yourpassword@localhost:5432/yourdbname
   ```
4. Delete `app.db` if it exists, and run `python run.py` again.

No code changes required — this is the entire point of using an ORM
instead of raw SQL tied to one database engine.

## API Reference

Identical to Task 2 — see the endpoint table and example `curl`
commands there. All routes, request formats, and status codes are
unchanged; only the storage layer changed.

| Resource | Endpoints |
|---|---|
| Users | `POST/GET /api/users`, `GET/DELETE /api/users/<id>` |
| Projects | `POST/GET /api/projects`, `GET /api/projects/<id>` |
| Tasks | `POST/GET /api/tasks`, `GET/PUT/DELETE /api/tasks/<id>`, `PATCH /api/tasks/<id>/status` |

## Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Flask secret key | `dev-only-insecure-key` |
| `FLASK_DEBUG` | Enable debug/auto-reload | `true` |
| `PORT` | Port the server listens on | `5000` |
| `DATABASE_URL` | Full DB connection string | unset → local SQLite file |

No credentials are ever hard-coded in source files — everything comes
from `.env`, which is git-ignored.

## Notes for Task 4

Task 4 wires this exact API up to the Task 1 dashboard (replacing its
`mockData.js`) and adds authentication, so `User` will gain a
password field and login endpoints at that point.

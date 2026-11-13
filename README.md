# KanMind Backend

KanMind is a Django REST Framework backend for a Kanban-style task management application.

This repository currently contains the backend foundation for boards, tasks, comments, and their relationships. The project is being developed as part of the Developer Akademie backend course.

> **Current status:** foundation / pre-project implementation. Authentication, authorization, Academy-specific endpoint contracts, and frontend integration will be added after the official project specification is reviewed.

## Tech Stack

- Python
- Django 5.2
- Django REST Framework 3.18
- SQLite
- Postman for API testing

## Current Domain Model

### Board
Fields: `id`, `title`, `owner`, `members`, `created_at`, `updated_at`

### Task
Fields: `id`, `title`, `description`, `board`, `assignee`, `reviewer`, `status`, `priority`, `due_date`, `created_at`, `updated_at`

Status values: `to-do`, `in-progress`, `review`, `done`

Priority values: `low`, `medium`, `high`

### Comment
Fields: `id`, `task`, `author`, `content`, `created_at`

## Current API

Base URL:

```text
http://127.0.0.1:8000/api/
```

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/boards/` | List boards |
| POST | `/api/boards/` | Create board |
| GET | `/api/boards/<id>/` | Retrieve board |
| PATCH | `/api/boards/<id>/` | Partially update board |
| DELETE | `/api/boards/<id>/` | Delete board |
| GET | `/api/tasks/` | List tasks |
| POST | `/api/tasks/` | Create task |
| GET | `/api/tasks/<id>/` | Retrieve task |
| PATCH | `/api/tasks/<id>/` | Partially update task |
| DELETE | `/api/tasks/<id>/` | Delete task |
| GET | `/api/comments/` | List comments |
| POST | `/api/comments/` | Create comment |
| GET | `/api/comments/<id>/` | Retrieve comment |
| PATCH | `/api/comments/<id>/` | Partially update comment |
| DELETE | `/api/comments/<id>/` | Delete comment |

Authentication and permissions are not implemented yet.

## Local Setup

```bash
git clone https://github.com/YvesGM/kanmind-backend-developer-academy.git
cd kanmind-backend-developer-academy
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Optional admin user:

```bash
python manage.py createsuperuser
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

## Example Requests

Create board:

```json
{
  "title": "KanMind Testboard",
  "owner": 1,
  "members": [1, 2]
}
```

Create task:

```json
{
  "title": "Implement login",
  "description": "Build the authentication endpoint",
  "board": 1,
  "assignee": 1,
  "reviewer": 2,
  "status": "to-do",
  "priority": "high",
  "due_date": "2026-11-20"
}
```

Move task:

```json
{
  "status": "in-progress"
}
```

Create comment:

```json
{
  "task": 1,
  "author": 1,
  "content": "Implementation has started."
}
```

## Postman

Import:

```text
postman/KanMind.postman_collection.json
```

Human-readable request sheet:

```text
docs/POSTMAN.md
```

Variables used by the collection:

- `baseUrl`
- `boardId`
- `taskId`
- `commentId`
- `ownerId`
- `memberId`

## Project Structure

```text
.
├── kan-mind-db/
├── kan_mind_app/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── docs/
│   └── POSTMAN.md
├── postman/
│   └── KanMind.postman_collection.json
├── manage.py
└── requirements.txt
```

## Development Notes

Expected next areas:

- registration and login
- authentication tokens
- permissions and board membership rules
- guest account behavior
- exact Academy request/response contracts
- task filters such as assigned-to-me and reviewing
- email lookup/check endpoint
- nested or enriched serializers where required
- frontend integration
- validation and automated tests

The backend should first be verified independently with Postman before frontend integration.

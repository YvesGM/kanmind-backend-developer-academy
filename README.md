# KanMind Backend

KanMind is a Django REST Framework backend for a Kanban-style task management application developed as part of the Developer Akademie backend course.

> **Current status:** Academy foundation. The backend already provides models, serializers, generic API views, token authentication, permissions, query filtering, admin configuration, and Postman documentation. Academy-specific response contracts will be aligned after the official KanMind project specification is reviewed.

## Tech Stack

- Python
- Django 5.2
- Django REST Framework 3.18
- DRF Token Authentication
- SQLite
- Postman

## Implemented Foundation

### Domain models

- `Board`
- `Task`
- `Comment`
- Django's built-in `User`

### Authentication

- registration by email/password
- login by email/password
- token creation
- logout/token invalidation
- email existence check

Authenticated requests use:

```text
Authorization: Token <token>
```

### Permissions

- API resources require authentication by default.
- Users only see boards they own or belong to.
- Board members may read boards.
- Only the board owner may update or delete a board.
- Tasks and comments are limited to accessible boards.
- Task assignees/reviewers must belong to the selected board.
- Comment authors are assigned from `request.user`.

### Query filtering

`GET /api/tasks/` supports:

```text
?board=<id>
?status=to-do
?priority=high
?assignee=<user-id>
?reviewer=<user-id>
```

Filters can be combined.

`GET /api/comments/` supports:

```text
?task=<task-id>
```

## API Endpoints

### Authentication

| Method | Endpoint | Purpose | Auth |
| --- | --- | --- | --- |
| POST | `/api/registration/` | Register and receive token | No |
| POST | `/api/login/` | Login and receive token | No |
| POST | `/api/logout/` | Invalidate current token | Yes |
| POST | `/api/email-check/` | Check whether email exists | No |

### Boards

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/boards/` | List accessible boards |
| POST | `/api/boards/` | Create board |
| GET | `/api/boards/<id>/` | Retrieve board |
| PATCH | `/api/boards/<id>/` | Update board |
| DELETE | `/api/boards/<id>/` | Delete board |

Board ownership is derived from the authenticated user and cannot be supplied by the client.

### Tasks

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/tasks/` | List/filter accessible tasks |
| POST | `/api/tasks/` | Create task |
| GET | `/api/tasks/<id>/` | Retrieve task |
| PATCH | `/api/tasks/<id>/` | Update task |
| DELETE | `/api/tasks/<id>/` | Delete task |

Allowed status values:

- `to-do`
- `in-progress`
- `review`
- `done`

Allowed priorities:

- `low`
- `medium`
- `high`

### Comments

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/comments/` | List/filter accessible comments |
| POST | `/api/comments/` | Create comment |
| GET | `/api/comments/<id>/` | Retrieve comment |
| PATCH | `/api/comments/<id>/` | Update comment |
| DELETE | `/api/comments/<id>/` | Delete comment |

The comment author is derived from the authenticated user.

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

`rest_framework.authtoken` adds database tables, so run `python manage.py migrate` after pulling the Academy foundation branch.

Optional admin user:

```bash
python manage.py createsuperuser
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

## Authentication Examples

### Registration

```json
{
  "email": "user@example.com",
  "password": "SecureExamplePassword123!",
  "repeated_password": "SecureExamplePassword123!"
}
```

### Login

```json
{
  "email": "user@example.com",
  "password": "SecureExamplePassword123!"
}
```

Successful registration/login returns a token and user summary.

## Domain Examples

### Create Board

```json
{
  "title": "KanMind Testboard",
  "members": [1, 2]
}
```

### Create Task

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

### Create Comment

```json
{
  "task": 1,
  "content": "Implementation has started."
}
```

## Postman

Import:

```text
postman/KanMind.postman_collection.json
```

Human-readable sheet:

```text
docs/POSTMAN.md
```

The collection stores the authentication token automatically after registration/login and sends it as `Authorization: Token {{token}}`.

## Project Structure

```text
.
├── kan-mind-db/
├── kan_mind_app/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── permissions.py
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

## Still intentionally pending

These areas depend on the official KanMind specification and are not guessed in advance:

- exact nested/enriched response structures
- `SerializerMethodField` values and dashboard aggregations
- dedicated `assigned-to-me` / `reviewing` endpoints
- exact guest account provisioning
- final registration/login response shape
- final object-level permission matrix
- frontend integration contract
- pagination/limit-offset requirements
- final automated test matrix

The API should be verified with Postman before frontend integration.

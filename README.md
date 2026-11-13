# KanMind Backend

KanMind is the Django REST Framework backend for the Developer Akademie KanMind project. It implements the API contract consumed by the supplied KanMind frontend.

## Tech Stack

- Python
- Django 5.2
- Django REST Framework 3.18
- DRF Token Authentication
- SQLite for local development
- Postman for API verification

## Project Structure

```text
.
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── kan_mind_app/
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── migrations/
│   ├── tests/
│   ├── admin.py
│   ├── apps.py
│   └── models.py
├── postman/
│   ├── KanMind.postman_collection.json
│   └── POSTMAN.md
├── manage.py
└── requirements.txt
```

## Local Setup

### 1. Clone and enter the repository

```bash
git clone https://github.com/YvesGM/kanmind-backend-developer-academy.git
cd kanmind-backend-developer-academy
```

### 2. Create and activate a virtual environment

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Optional: create an admin user

```bash
python manage.py createsuperuser
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

### 6. Start the development server

```bash
python manage.py runserver
```

API base URL:

```text
http://127.0.0.1:8000/api/
```

The supplied frontend is started with Live Server and therefore runs on a
different origin. CORS responses are enabled while Django runs with
`DEBUG=True`; production deployments should configure explicit origins.

## Authentication

KanMind uses DRF token authentication.

Authenticated requests require:

```text
Authorization: Token <token>
```

### Registration

```http
POST /api/registration/
```

```json
{
  "fullname": "Example Username",
  "email": "example@mail.de",
  "password": "examplePassword",
  "repeated_password": "examplePassword"
}
```

Response:

```json
{
  "token": "<token>",
  "fullname": "Example Username",
  "email": "example@mail.de",
  "user_id": 123
}
```

### Login

```http
POST /api/login/
```

The response has the same flat authentication shape as registration.

### Frontend guest account

The supplied frontend uses a normal login request for its guest account. Create a matching Django user for the credentials configured in the frontend file:

```text
shared/js/config.js
```

The backend does not hard-code guest credentials.

## API Overview

### User lookup

```http
GET /api/email-check/?email=<email>
```

Authentication is required. Existing users are returned as:

```json
{
  "id": 1,
  "email": "max.mustermann@example.com",
  "fullname": "Max Mustermann"
}
```

### Boards

```text
GET    /api/boards/
POST   /api/boards/
GET    /api/boards/<board_id>/
PATCH  /api/boards/<board_id>/
DELETE /api/boards/<board_id>/
```

Board list responses include:

- `member_count`
- `ticket_count`
- `tasks_to_do_count`
- `tasks_high_prio_count`
- `owner_id`

Board detail responses include nested members and tasks.

Permissions:

- owner or member: read board
- owner or member: update board title/member list
- owner only: delete board

### Tasks

```text
POST   /api/tasks/
PATCH  /api/tasks/<task_id>/
DELETE /api/tasks/<task_id>/
GET    /api/tasks/assigned-to-me/
GET    /api/tasks/reviewing/
```

Task write requests use `assignee_id` and `reviewer_id`. Responses expose nested `assignee` and `reviewer` objects.

Supported statuses:

```text
to-do
in-progress
review
done
```

Supported priorities:

```text
low
medium
high
```

Task rules:

- only board owners/members may create or update tasks
- assignee and reviewer must belong to the board
- the board relation cannot be changed by PATCH
- only the task creator or board owner may delete a task

### Comments

```text
GET    /api/tasks/<task_id>/comments/
POST   /api/tasks/<task_id>/comments/
DELETE /api/tasks/<task_id>/comments/<comment_id>/
```

The comment author is derived from the authenticated user. Only the comment author may delete the comment.

## Database and Repository Hygiene

The local SQLite database is intentionally ignored by Git.

Also ignored:

- virtual environments
- `.env`
- Python bytecode
- editor-specific files

The default development secret key is only a local fallback. Set a real key through:

```bash
export DJANGO_SECRET_KEY='your-development-key'
```

## Tests

Run the Django test suite with:

```bash
python manage.py test
```

The project includes API tests for authentication, boards, tasks, comments, validation, and permissions.

Before submission, verify the complete API against the Developer Akademie PM tests and the required coverage target.

## Postman

Import:

```text
postman/KanMind.postman_collection.json
```

The imported hierarchy is:

```text
Developer Academy
└── KanMind
    ├── Authentication
    ├── Boards
    ├── Tasks
    ├── Comments
    └── Negative Tests
```

Detailed usage is documented in:

```text
postman/POSTMAN.md
```

## Frontend

The supplied frontend repository is:

```text
YvesGM/dev-academy-project.KanMind
```

The backend is intentionally kept in its own repository, as required by the Developer Akademie checklist.

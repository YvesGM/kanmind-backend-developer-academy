# KanMind Postman Guide

The collection mirrors the official KanMind endpoint contract.

## Import

Import:

```text
postman/KanMind.postman_collection.json
```

Expected hierarchy:

```text
Developer Academy
└── KanMind
    ├── Authentication
    ├── Boards
    ├── Tasks
    ├── Comments
    └── Negative Tests
```

## Collection Variables

```text
baseUrl       http://127.0.0.1:8000/api
token         current authentication token
ownerEmail    owner@example.com
ownerPassword StrongPassword123!
memberEmail   member@example.com
memberPassword StrongPassword123!
ownerId       set automatically
memberId      set automatically
boardId       set automatically
taskId        set automatically
commentId     set automatically
```

The KanMind folder injects:

```text
Authorization: Token {{token}}
```

Registration and login remove this header before sending the request.

## Recommended Run Order

1. Register Owner
2. Register Member
3. Login Owner
4. Email Check Member
5. Create Board
6. List Boards
7. Get Board
8. Patch Board
9. Create Task
10. Assigned To Me
11. Reviewing
12. Patch Task
13. Create Comment
14. List Comments
15. Delete Comment
16. Delete Task
17. Delete Board
18. Run Negative Tests

## Official Endpoints

### Authentication

```text
POST /registration/
POST /login/
GET  /email-check/?email=<email>
```

### Boards

```text
GET    /boards/
POST   /boards/
GET    /boards/{{boardId}}/
PATCH  /boards/{{boardId}}/
DELETE /boards/{{boardId}}/
```

### Tasks

```text
POST   /tasks/
PATCH  /tasks/{{taskId}}/
DELETE /tasks/{{taskId}}/
GET    /tasks/assigned-to-me/
GET    /tasks/reviewing/
```

### Comments

```text
GET    /tasks/{{taskId}}/comments/
POST   /tasks/{{taskId}}/comments/
DELETE /tasks/{{taskId}}/comments/{{commentId}}/
```

## Request Shapes

### Registration

```json
{
  "fullname": "Owner User",
  "email": "{{ownerEmail}}",
  "password": "{{ownerPassword}}",
  "repeated_password": "{{ownerPassword}}"
}
```

### Create Board

```json
{
  "title": "KanMind Testboard",
  "members": [{{memberId}}]
}
```

### Patch Board

```json
{
  "title": "Changed title",
  "members": [{{memberId}}]
}
```

### Create Task

```json
{
  "board": {{boardId}},
  "title": "Code review",
  "description": "Review the new pull request",
  "status": "review",
  "priority": "medium",
  "assignee_id": {{memberId}},
  "reviewer_id": {{ownerId}},
  "due_date": "2026-12-15"
}
```

### Patch Task

Do not send `board` during PATCH.

```json
{
  "title": "Code review finished",
  "status": "done",
  "priority": "high",
  "assignee_id": {{memberId}},
  "reviewer_id": {{ownerId}},
  "due_date": "2026-12-16"
}
```

### Create Comment

```json
{
  "content": "This is a task comment."
}
```

## Important Permission Tests

Verify at least:

- unauthenticated protected request → 401
- board outsider → 403/404 according to resource visibility
- board member may PATCH board
- board member may not DELETE board
- non-member cannot become assignee/reviewer
- task board cannot be changed by PATCH
- board member who is neither creator nor owner cannot DELETE task
- non-author cannot DELETE comment
- unknown resources → 404
- invalid status/priority → 400

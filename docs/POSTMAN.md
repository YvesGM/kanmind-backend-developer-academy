# KanMind Postman Sheet

This documents the current **Academy foundation branch**.

## Variables

```text
{{baseUrl}} = http://127.0.0.1:8000/api
{{token}} = set automatically after login/registration
{{boardId}} = set automatically after board creation
{{taskId}} = set automatically after task creation
{{commentId}} = set automatically after comment creation
{{memberId}} = ID of another registered board member
```

Authenticated requests require:

```text
Authorization: Token {{token}}
```

## Recommended Test Order

1. Registration
2. Email check
3. Create a second user if member/assignee tests are required.
4. Login as the main user.
5. Create Board.
6. List/Get/Patch Board.
7. Create Task.
8. Filter/List/Get/Patch Task.
9. Create Comment.
10. Filter/List/Get/Patch Comment.
11. Permission/negative tests.
12. Delete Comment, Task, Board.
13. Logout.

## Authentication

### Register

`POST {{baseUrl}}/registration/`

```json
{
  "email": "kanmind-owner@example.com",
  "password": "SecureExamplePassword123!",
  "repeated_password": "SecureExamplePassword123!"
}
```

Expected: `201 Created`

### Login

`POST {{baseUrl}}/login/`

```json
{
  "email": "kanmind-owner@example.com",
  "password": "SecureExamplePassword123!"
}
```

Expected: `200 OK`

### Email Check

`POST {{baseUrl}}/email-check/`

```json
{
  "email": "kanmind-owner@example.com"
}
```

Example:

```json
{
  "exists": true
}
```

### Logout

`POST {{baseUrl}}/logout/`

Expected: `204 No Content`

## Boards

### Create

`POST {{baseUrl}}/boards/`

```json
{
  "title": "KanMind Testboard",
  "members": []
}
```

Expected: `201 Created`

The authenticated user becomes owner automatically and is automatically added to members.

### List

`GET {{baseUrl}}/boards/`

Only boards owned by or shared with the authenticated user are returned.

### Detail

`GET {{baseUrl}}/boards/{{boardId}}/`

### Patch

`PATCH {{baseUrl}}/boards/{{boardId}}/`

```json
{
  "title": "KanMind Backend Board"
}
```

Only the board owner may mutate the board.

### Delete

`DELETE {{baseUrl}}/boards/{{boardId}}/`

Expected: `204 No Content`

## Tasks

### Create

`POST {{baseUrl}}/tasks/`

```json
{
  "title": "Implement login",
  "description": "Build the authentication endpoint",
  "board": {{boardId}},
  "assignee": null,
  "reviewer": null,
  "status": "to-do",
  "priority": "high",
  "due_date": "2026-11-20"
}
```

Expected: `201 Created`

Assignee/reviewer must be owner or member of the selected board.

### Filter

Examples:

```text
GET {{baseUrl}}/tasks/?status=to-do
GET {{baseUrl}}/tasks/?priority=high
GET {{baseUrl}}/tasks/?board={{boardId}}
GET {{baseUrl}}/tasks/?assignee={{memberId}}
GET {{baseUrl}}/tasks/?reviewer={{memberId}}
GET {{baseUrl}}/tasks/?board={{boardId}}&status=in-progress&priority=high
```

### Patch

`PATCH {{baseUrl}}/tasks/{{taskId}}/`

```json
{
  "status": "in-progress"
}
```

### Delete

`DELETE {{baseUrl}}/tasks/{{taskId}}/`

Expected: `204 No Content`

## Comments

### Create

`POST {{baseUrl}}/comments/`

```json
{
  "task": {{taskId}},
  "content": "Implementation has started."
}
```

The author is assigned from the authenticated user.

### Filter

```text
GET {{baseUrl}}/comments/?task={{taskId}}
```

### Patch

`PATCH {{baseUrl}}/comments/{{commentId}}/`

```json
{
  "content": "Updated comment."
}
```

## Negative Tests

### Missing authentication

Call `GET {{baseUrl}}/boards/` without the Token header.

Expected: `401 Unauthorized` or authentication failure depending on the active authentication class/request context.

### Invalid login

Expected: `400 Bad Request`.

### Duplicate registration email

Expected: `400 Bad Request`.

### Password mismatch

Expected: `400 Bad Request`.

### Invalid task status

```json
{
  "status": "banana"
}
```

Expected: `400 Bad Request`.

### Invalid board assignment

Create/update a task for a board the authenticated user cannot access.

Expected: `400 Bad Request` or `403 Forbidden`, depending on whether validation or object permission rejects the request first.

### Non-member assignee/reviewer

Expected: `400 Bad Request`.

### Non-owner board update

Expected: `403 Forbidden` or an inaccessible-object `404`, depending on queryset visibility.

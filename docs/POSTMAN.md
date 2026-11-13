# KanMind Postman Sheet

Current implementation only; not yet the final Academy contract.

## Variables

```text
{{baseUrl}} = http://127.0.0.1:8000/api
{{ownerId}} = 1
{{memberId}} = 2
{{boardId}} = 1
{{taskId}} = 1
{{commentId}} = 1
```

## Recommended order

1. Verify/create users in Django Admin.
2. Create Board.
3. List/Get/Patch Board.
4. Create Task.
5. List/Get/Patch Task.
6. Create Comment.
7. List/Get/Patch Comment.
8. Delete Comment, Task, Board.

## Boards

### GET list
`GET {{baseUrl}}/boards/`

Expected: `200 OK`

### POST create
`POST {{baseUrl}}/boards/`

```json
{
  "title": "KanMind Testboard",
  "owner": {{ownerId}},
  "members": [{{ownerId}}, {{memberId}}]
}
```

Expected: `201 Created`

### GET detail
`GET {{baseUrl}}/boards/{{boardId}}/`

Expected: `200 OK`, unknown ID: `404 Not Found`

### PATCH
`PATCH {{baseUrl}}/boards/{{boardId}}/`

```json
{
  "title": "KanMind Backend Board"
}
```

Expected: `200 OK`

### DELETE
`DELETE {{baseUrl}}/boards/{{boardId}}/`

Expected: `204 No Content`

## Tasks

### GET list
`GET {{baseUrl}}/tasks/`

Expected: `200 OK`

### POST create
`POST {{baseUrl}}/tasks/`

```json
{
  "title": "Implement login",
  "description": "Build the authentication endpoint",
  "board": {{boardId}},
  "assignee": {{ownerId}},
  "reviewer": {{memberId}},
  "status": "to-do",
  "priority": "high",
  "due_date": "2026-11-20"
}
```

Expected: `201 Created`

Allowed status: `to-do`, `in-progress`, `review`, `done`

Allowed priority: `low`, `medium`, `high`

### GET detail
`GET {{baseUrl}}/tasks/{{taskId}}/`

### PATCH move
`PATCH {{baseUrl}}/tasks/{{taskId}}/`

```json
{
  "status": "in-progress"
}
```

### PATCH assignment

```json
{
  "assignee": {{memberId}},
  "reviewer": {{ownerId}}
}
```

### DELETE
`DELETE {{baseUrl}}/tasks/{{taskId}}/`

Expected: `204 No Content`

## Comments

### GET list
`GET {{baseUrl}}/comments/`

### POST create
`POST {{baseUrl}}/comments/`

```json
{
  "task": {{taskId}},
  "author": {{ownerId}},
  "content": "Implementation has started."
}
```

Expected: `201 Created`

### GET detail
`GET {{baseUrl}}/comments/{{commentId}}/`

### PATCH
`PATCH {{baseUrl}}/comments/{{commentId}}/`

```json
{
  "content": "Implementation has started and the first endpoint is working."
}
```

### DELETE
`DELETE {{baseUrl}}/comments/{{commentId}}/`

Expected: `204 No Content`

## Negative tests

Unknown board:

`GET {{baseUrl}}/boards/999999/` → `404`

Invalid status:

```json
{
  "status": "banana"
}
```

→ `400`

Invalid priority:

```json
{
  "priority": "critical"
}
```

→ `400` with the current model.

Invalid relation:

```json
{
  "title": "Broken relation test",
  "board": 999999
}
```

→ `400`

## Current limitations

Not implemented yet:

- authentication
- authorization/permissions
- automatic `request.user`
- board-member validation
- assigned-to-me/reviewing
- email check
- guest login

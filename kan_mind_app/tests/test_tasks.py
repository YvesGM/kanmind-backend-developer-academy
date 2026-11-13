from rest_framework import status

from kan_mind_app.tests.base import KanMindAPITestCase


class TaskAPITests(KanMindAPITestCase):
    """Verify task creation, dashboard endpoints, and permissions."""

    def task_payload(self):
        return {
            'board': self.board.id,
            'title': 'Code review',
            'description': 'Review PR',
            'status': 'review',
            'priority': 'high',
            'assignee_id': self.member.id,
            'reviewer_id': self.owner.id,
            'due_date': '2026-12-15',
        }

    def test_create_task_returns_nested_people(self):
        response = self.client.post('/api/tasks/', self.task_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['assignee']['id'], self.member.id)
        self.assertEqual(response.data['reviewer']['id'], self.owner.id)

    def test_assigned_to_me_returns_only_assigned_tasks(self):
        self.create_task(assignee=self.owner)
        self.create_task(title='Other', assignee=self.member)
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_reviewing_returns_reviewer_tasks(self):
        self.create_task(reviewer=self.owner)
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['reviewer']['id'], self.owner.id)

    def test_patch_cannot_change_board(self):
        task = self.create_task()
        response = self.client.patch(
            f'/api/tasks/{task.id}/', {'board': self.board.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_member_cannot_be_assignee(self):
        payload = self.task_payload()
        payload['assignee_id'] = self.outsider.id
        response = self.client.post('/api/tasks/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_board_member_cannot_delete_foreign_task(self):
        task = self.create_task()
        self.authenticate(self.member)
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_gets_forbidden_for_existing_task(self):
        task = self.create_task()
        self.authenticate(self.outsider)
        response = self.client.patch(
            f'/api/tasks/{task.id}/', {'status': 'done'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_create_task_on_board(self):
        self.authenticate(self.outsider)
        response = self.client.post('/api/tasks/', self.task_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

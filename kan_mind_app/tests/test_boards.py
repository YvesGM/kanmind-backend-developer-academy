from rest_framework import status

from kan_mind_app.models import Comment
from kan_mind_app.tests.base import KanMindAPITestCase


class BoardAPITests(KanMindAPITestCase):
    """Verify board shapes, counts, and permissions."""

    def test_board_list_contains_required_counts(self):
        task = self.create_task(status='to-do', priority='high')
        Comment.objects.create(task=task, author=self.owner, content='Comment')
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ticket_count'], 1)
        self.assertEqual(response.data[0]['tasks_high_prio_count'], 1)

    def test_create_board_sets_authenticated_owner(self):
        response = self.client.post(
            '/api/boards/', {'title': 'New', 'members': [self.member.id]}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner_id'], self.owner.id)

    def test_member_can_patch_board(self):
        self.authenticate(self.member)
        response = self.client.patch(
            f'/api/boards/{self.board.id}/', {'title': 'Changed'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Changed')

    def test_member_cannot_delete_board(self):
        self.authenticate(self.member)
        response = self.client.delete(f'/api/boards/{self.board.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_board(self):
        response = self.client.delete(f'/api/boards/{self.board.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

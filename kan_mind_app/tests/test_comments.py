from rest_framework import status

from kan_mind_app.models import Comment
from kan_mind_app.tests.base import KanMindAPITestCase


class CommentAPITests(KanMindAPITestCase):
    """Verify nested comment endpoints and author permissions."""

    def test_create_comment_uses_authenticated_author(self):
        task = self.create_task()
        response = self.client.post(
            f'/api/tasks/{task.id}/comments/',
            {'content': 'New comment'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], 'Owner User')

    def test_comments_are_nested_under_task(self):
        task = self.create_task()
        Comment.objects.create(task=task, author=self.owner, content='One')
        response = self.client.get(f'/api/tasks/{task.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['content'], 'One')

    def test_only_author_can_delete_comment(self):
        task = self.create_task()
        comment = Comment.objects.create(task=task, author=self.owner, content='One')
        self.authenticate(self.member)
        url = f'/api/tasks/{task.id}/comments/{comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from kan_mind_app.models import Board, Task

User = get_user_model()


class KanMindAPITestCase(APITestCase):
    """Provide reusable authenticated KanMind test data."""

    def setUp(self):
        self.owner = self.create_user('owner@example.com', 'Owner User')
        self.member = self.create_user('member@example.com', 'Member User')
        self.outsider = self.create_user('outsider@example.com', 'Outside User')
        self.board = Board.objects.create(title='Project X', owner=self.owner)
        self.board.members.add(self.member)
        self.authenticate(self.owner)

    def create_user(self, email, fullname):
        return User.objects.create_user(
            username=email,
            email=email,
            first_name=fullname,
            password='StrongPassword123!',
        )

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def create_task(self, creator=None, **kwargs):
        defaults = {
            'title': 'Task',
            'board': self.board,
            'creator': creator or self.owner,
            'due_date': '2026-12-01',
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)

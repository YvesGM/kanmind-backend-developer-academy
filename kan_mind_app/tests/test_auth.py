from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class AuthenticationTests(APITestCase):
    """Verify registration, login, and authenticated email lookup."""

    def test_registration_returns_expected_shape(self):
        payload = {
            'fullname': 'Example User',
            'email': 'example@mail.de',
            'password': 'StrongPassword123!',
            'repeated_password': 'StrongPassword123!',
        }
        response = self.client.post('/api/registration/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data), {'token', 'fullname', 'email', 'user_id'})

    def test_login_returns_expected_shape(self):
        user = User.objects.create_user(
            username='login@mail.de',
            email='login@mail.de',
            first_name='Login User',
            password='StrongPassword123!',
        )
        payload = {'email': user.email, 'password': 'StrongPassword123!'}
        response = self.client.post('/api/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['fullname'], 'Login User')

    def test_email_check_requires_authentication(self):
        response = self.client.get('/api/email-check/?email=test@mail.de')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_email_check_returns_user(self):
        user = User.objects.create_user(username='u@mail.de', email='u@mail.de')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get('/api/email-check/?email=u@mail.de')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)

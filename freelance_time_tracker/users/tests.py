from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from users.models import CustomUser
from rest_framework import status
import pytest


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    def create_user(**kwargs):
        return CustomUser.objects.create_user(**kwargs)
    return create_user


@pytest.mark.django_db
class TestUserAPI:
    signup_url = '/users/api/signup/'
    login_url = '/users/api/login/'
    logout_url = '/users/api/logout/'

    def test_signup_success(self, client):
        """
        Test the signup endpoint for successful user registration.
        """
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'strongpassword123'
        }
        response = client.post(self.signup_url, data, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response_data
        assert response_data['user']['username'] == data['username']
        assert response_data['user']['email'] == data['email']
        assert 'access' in response_data
        assert 'refresh' in response_data

    def test_signup_failure_missing_field(self, client):
        """
        Test the signup endpoint for missing required fields.
        """
        data = {
            'username': 'testuser',
            'password': 'strongpassword123'
        }
        response = client.post(self.signup_url, data, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response_data

    def test_login_success(self, client, user_factory):
        """
        Test the login endpoint for successful user authentication.
        """
        user = user_factory(
            username='loginuser', email='login@example.com', password='secret'
        )
        data = {
            'email': 'login@example.com',
            'password': 'secret'
        }
        response = client.post(self.login_url, data, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response_data
        assert response_data['user']['username'] == user.username
        assert 'access' in response_data
        assert 'refresh' in response_data

    def test_login_failure_invalid_password(self, client, user_factory):
        """
        Test the login endpoint for invalid password.
        """
        user_factory(
            username='loginuser', email='login@example.com', password='secret'
        )
        data = {
            'email': 'login@example.com',
            'password': 'wrongpassword'
        }
        response = client.post(self.login_url, data, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data.get('detail') == "Invalid credentials"

    def test_login_failure_nonexistent_user(self, client):
        """
        Test the login endpoint for a nonexistent user.
        """
        data = {
            'email': 'nonexistent@example.com',
            'password': 'secret'
        }
        response = client.post(self.login_url, data, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data.get('detail') == "Invalid credentials"

    def test_logout_success(self, client, user_factory):
        """
        Test the logout endpoint for successful user logout.
        """
        user = user_factory(
            username='logoutuser',
            email='logout@example.com',
            password='secret'
        )
        refresh = RefreshToken.for_user(user)
        client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
        )
        data = {
            'refresh': str(refresh)
        }
        response = client.post(self.logout_url, data, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data.get('detail') == "Successfully logged out"

    def test_logout_failure_missing_refresh_token(self, client, user_factory):
        """
        Test the logout endpoint for missing refresh token.
        """
        user = user_factory(
            username='logoutuser',
            email='logout@example.com',
            password='secret'
        )
        refresh = RefreshToken.for_user(user)
        client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
        )
        data = {}
        response = client.post(self.logout_url, data, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_data.get('error') == "Refresh token is required"

    def test_logout_failure_invalid_refresh_token(self, client, user_factory):
        """
        Test the logout endpoint for invalid refresh token.
        """
        user = user_factory(
            username='logoutuser',
            email='logout@example.com',
            password='secret'
        )
        refresh = RefreshToken.for_user(user)
        client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
        )
        data = {
            'refresh': 'invalidtoken'
        }
        response = client.post(self.logout_url, data, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_data.get('error') == "Invalid or expired token"

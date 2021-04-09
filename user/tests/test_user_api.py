from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# URL ##
CREATE_USER_URL = reverse('user:create')
Token_URL = reverse('user:token')


def create_user(**param):
    return get_user_model().objects.create_user(**param)


class PublicUserApiTest(TestCase):
    """Test the user API public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """User with valid payload successful"""
        payload = {
            'email': "abc@gmail.com",
            'password': 'testcase',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test that existing user creation failed"""
        payload = {
            'email': 'abc@gmail.com',
            'password': 'tetcase',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Testpassword must be more than 5 characters"""
        payload = {'email': 'abc@gmail.com', 'password': 'pw'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    # Token Create and Validation Test
    def test_create_token_for_user(self):
        """Test that token created for user"""
        payload = {'email': 'abc@gmail.com', 'password': 'testcase'}
        create_user(**payload)
        res = self.client.post(Token_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_data_fail(self):
        """Test that token created with invalid credential fail"""
        create_user(email='abc@gmail.com', password='testpass')
        payload = {'email': 'abc@gmail.com', 'password': 'wrongpass'}
        res = self.client.post(Token_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_a_user(self):
        """Test that token create without a user fails"""
        payload = {'email': 'abc@g.com', 'password': 'testpass'}
        res = self.client.post(Token_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_missing_field_fail(self):
        """Test Create token with missing field fail"""
        res = self.client.post(Token_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# URL ##
CREATE_USER_URL = reverse('user:create')
Token_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    # Make authentication mandatory
    def test_retrieve_user_unauthorized(self):
        """Test Authentication is required for user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API request that requires authentication"""
    def setUp(self):
        self.user = create_user(
            email='abc@gmail.com',
            password='testpass',
            name='test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user success"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed(self):
        """Test that post is not allowed"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for authenticated user"""
        payload = {
            'name': 'new name',
            'password': 'newpass'
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

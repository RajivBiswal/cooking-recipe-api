from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='abc@gmail.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_success(self):
        "Test creating user with email is successful"
        email = 'abc@gmail.com'
        password = 'testpass'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'abc@gmail.com'
        user = get_user_model().objects.create_user(email, 'testpass')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raise error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpass')

    def test_create_new_superuser(self):
        """Test creating new superuser"""
        user = get_user_model().objects.create_superuser(
            'abc@gmail.com',
            'testpass'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # Tag app Test models
    def test_tag_str(self):
        """creating a tag  from models and test string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber',
        )
        self.assertEqual(str(ingredient), ingredient.name)

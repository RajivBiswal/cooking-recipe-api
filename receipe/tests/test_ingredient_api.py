from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from receipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('receipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the public ingredients"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that logi required for access enpoints"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsTest(TestCase):
    """Test ingredient for authenticated user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'abc@gmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """test retrieving list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Lily')
        Ingredient.objects.create(user=self.user, name='Haze')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients are limited to authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'newpass'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Turmeric')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Create new ingredient successfully"""
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_invalid_ingredient_fail(self):
        """Test creating invalid ingredient fail"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredient_assigned_to_recipe(self):
        """Test retrieving ingredient assigned to recipe"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='potato')
        ingredient2 = Ingredient.objects.create(user=self.user, name='tomato')
        recipe = Recipe.objects.create(
            title='Potato Chips',
            time_minutes=45,
            price=20,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrive_ingredients_assigned_unique(self):
        """Test that retrieve unique ingredient assigned to recipe"""
        ingredient = Ingredient.objects.create(user=self.user, name='potato')
        Ingredient.objects.create(user=self.user, name='waste')
        recipe = Recipe.objects.create(
            title='Potato ball',
            time_minutes=20,
            price=50,
            user=self.user
        )
        recipe.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Wasted',
            time_minutes=10,
            price=2,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

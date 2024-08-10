"""Test for the ingredient API"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient


from core.models import (
    Ingredient,
    Recipe,
)
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """Create and return ingredient detail url"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="user@example.com", password="test123_"):
    """Create and return new user"""
    return get_user_model().objects.create_user(email, password)


class PublicIngredientAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required for retrieving ingredients"""

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving ingredient list"""

        Ingredient.objects.create(
            user=self.user,
            name="Chocolate",
        )

        Ingredient.objects.create(
            user=self.user,
            name="Vanilla",
        )

        response = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredient_limited_to_auth_user(self):
        """Test list of ingredient returned is limited to authenticated user"""

        user2 = create_user(email="user2@example.com")
        Ingredient.objects.create(user=user2, name="Carotte")

        ingredient = Ingredient.objects.create(user=self.user, name="Pepper")

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], ingredient.name)
        self.assertEqual(response.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        """Test updating ingredient"""

        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Salt",
        )

        payload = {"name": "Sugar"}
        url = detail_url(ingredient_id=ingredient.id)

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test deleting existing ingredient"""

        ingredient = Ingredient.objects.create(user=self.user, name="Cassava")
        url = detail_url(ingredient_id=ingredient.id)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipe(self):
        """Test listing ingredients by those assigned to recipes"""

        in1 = Ingredient.objects.create(user=self.user, name="Apple")
        in2 = Ingredient.objects.create(user=self.user, name="Banana")

        recipe = Recipe.objects.create(
            title="Apple cream",
            time_minutes=9,
            price=Decimal("10.3"),
            user=self.user,
        )

        recipe.ingredients.add(in1)

        response = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        self.assertIn(s1.data, response.data)
        self.assertNotIn(s2.data, response.data)

    def test_filtered_ingredients_unique(self):
        """Test filter ingredients return unique list"""

        ing = Ingredient.objects.create(user=self.user, name="Eggs")
        Ingredient.objects.create(user=self.user, name="Menthe")

        recipe1 = Recipe.objects.create(
            title="Soft eggs",
            time_minutes=9,
            price=Decimal("91.1"),
            user=self.user,
        )

        recipe2 = Recipe.objects.create(
            title="Not soft eggs",
            time_minutes=19,
            price=Decimal("41.1"),
            user=self.user,
        )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        response = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(len(response.data), 1)

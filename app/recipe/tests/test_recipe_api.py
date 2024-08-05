"""
Test for recipe apis

"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse("recipe:recipe-list")


def create_recipe(user, **params):
    """Create and return recipe"""

    defaults = {
        "title": "Sample recipe test",
        "description": "Sample recipe description",
        "time_minutes": 10,
        "price": Decimal("5.8"),
        "link": "https://samplelink.com/recipe.pdf",
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthorized API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call recipe API"""

        response = self.client.get(RECIPE_URL)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API call"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@example.com",
            "password",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test recipe is limited to authenticated user"""

        other_user = get_user_model().objects.create_user(
            "other@example.com",
            "passfd20234_",
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        respone = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(respone.status_code, status.HTTP_200_OK)
        self.assertEqual(respone.data, serializer.data)

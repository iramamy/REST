"""
Test for recipe APIs

"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPE_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Create and return recipe detail ULR"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


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


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(
            email="test@example.com",
            password="testpassword",
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

        other_user = create_user(
            email="other@example.com",
            password="testpassword",
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        respone = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(respone.status_code, status.HTTP_200_OK)
        self.assertEqual(respone.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe_id=recipe.id)
        respone = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(respone.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""

        payload = {
            "title": "Sample recipe title",
            "time_minutes": 90,
            "price": Decimal("8.19"),
        }

        response = self.client.post(RECIPE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data["id"])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe"""

        original_link = "https://example.com/recipe/recipe.pdf"

        recipe = create_recipe(
            user=self.user,
            title="Sample title",
            link=original_link,
        )

        payload = {"title": "New sample title"}
        url = detail_url(recipe_id=recipe.id)

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Full update of a recipe"""

        recipe = create_recipe(
            user=self.user,
            title="Sample title",
            time_minutes=12,
            price=Decimal("9.21"),
            description="Sample description",
            link="https://example.com/recipe.pdf",
        )

        payload = {
            "title": "updated title",
            "time_minutes": 123,
            "price": Decimal("10.81"),
            "description": "Updated sample description",
            "link": "https://example.com/updated-recipe.pdf",
        }

        url = detail_url(recipe_id=recipe.id)

        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_update_user_return_error(self):
        """Test changing recipe user return error"""

        new_user = create_user(
            email="newuser@example.com",
            password="test123",
        )

        recipe = create_recipe(user=self.user)

        payload = {"user": new_user.id}

        url = detail_url(recipe_id=recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test delete recipe success"""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_user_recipe(self):
        """Test trying to delete othere users recipe"""

        other_user = create_user(
            email="other@example.com",
            password="123test_",
        )

        recipe = create_recipe(user=other_user)

        url = detail_url(recipe_id=recipe.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

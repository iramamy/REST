"""
Test for recipe APIs

"""

from decimal import Decimal
import os
import tempfile

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPE_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Create and return recipe detail ULR"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


def image_upload_url(recipe_id):
    """Create and return an image upload url"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


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

    # Test for tags
    def test_create_recipe_with_new_tags(self):
        """Test creating new recipe with new tags"""

        payload = {
            "title": "New recipe",
            "time_minutes": 43,
            "price": Decimal("5.4"),
            "tags": [{"name": "Tag1"}, {"name": "Tag2"}],
        }

        response = self.client.post(RECIPE_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = Tag.objects.filter(
                user=self.user,
                name=tag["name"],
            ).exists()

            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating new recipe with existing tags"""

        tag_indian = Tag.objects.create(
            user=self.user,
            name="Indian",
        )

        payload = {
            "title": "Recipe from India",
            "time_minutes": 13,
            "price": Decimal("19.23"),
            "tags": [{"name": "Indian"}, {"name": "tag 1"}],
        }

        response = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())

        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                user=self.user,
                name=tag["name"],
            ).exists()

            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Create new tag on update"""

        recipe = create_recipe(user=self.user)

        payload = {"tags": [{"name": "super"}]}

        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_tag = Tag.objects.get(user=self.user, name="super")
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existsing tag when updating a recipe"""

        tag_breakfast = Tag.objects.create(user=self.user, name="breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name="lunch")
        payload = {"tags": [{"name": "lunch"}]}

        url = detail_url(recipe_id=recipe.id)

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing tags assigned to recipe"""

        tag = Tag.objects.create(user=self.user, name="Bio Food")
        recipe = create_recipe(user=self.user)

        recipe.tags.add(tag)

        payload = {"tags": []}
        url = detail_url(recipe_id=recipe.id)

        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(tag, recipe.tags.all())

    # Test for ingredients
    def test_new_recipe_with_ingredients(self):
        """Test create recipe with ingredients"""

        payload = {
            "title": "Recipe from Japan",
            "time_minutes": 13,
            "price": Decimal("19.23"),
            "ingredients": [{"name": "sugar"}, {"name": "salt"}],
        }

        response = self.client.post(RECIPE_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"],
                user=self.user,
            ).exists()

            self.assertTrue(exists)

    def test_recipe_with_existing_ingredient(self):
        """Test creating recipe with existsing ingredient"""

        ingredients = Ingredient.objects.create(
            user=self.user,
            name="Pepper",
        )

        payload = {
            "title": "Recipe from Vietnam",
            "time_minutes": 40,
            "price": Decimal("59.23"),
            "ingredients": [{"name": "Pepper"}, {"name": "ingredient 1"}],
        }

        response = self.client.post(RECIPE_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredients, recipe.ingredients.all())

        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                user=self.user,
                name=ingredient["name"],
            ).exists()

            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating ingredient on updating a recipe"""

        recipe = create_recipe(user=self.user)
        payload = {"ingredients": [{"name": "Lemon"}]}
        url = detail_url(recipe_id=recipe.id)

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_ingredient = Ingredient.objects.get(
            user=self.user,
            name="Lemon",
        )
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating recipe"""

        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name="Pepper",
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name="Chili",
        )
        payload = {"ingredients": [{"name": "Chili"}]}

        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredient(self):
        """Test to clear a recipes ingredients"""

        ingredient = Ingredient.objects.create(
            user=self.user,
            name="garlic",
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {"ingredients": []}
        url = detail_url(recipe_id=recipe.id)

        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)


class ImageUploadTest(TestCase):
    """Tests for the image upload API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com",
            "testpass123_",
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe"""
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix=".jpeg") as img_file:
            img = Image.new("RGB", (10, 10))
            img.save(img_file, format="JPEG")
            img_file.seek(0)
            payload = {"image": img_file}
            response = self.client.post(url, payload, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image"""

        url = image_upload_url(self.recipe.id)
        payload = {"image": "notanimage"}

        response = self.client.post(url, payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

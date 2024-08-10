"""Test for the tags API"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAG_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """Create and return a tag detail"""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="test@example.com", password="testpass1234_"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


class PublicTagsAPITests(TestCase):
    """Test for unauthenticated user to make an API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to retrieve tags"""

        response = self.client.get(TAG_URL)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class PrivateTagsAPITests(TestCase):
    """Test for authenticated user to make an API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieve list of tags"""

        Tag.objects.create(user=self.user, name="Tag1")
        Tag.objects.create(user=self.user, name="Tag2")

        response = self.client.get(TAG_URL)
        tags = Tag.objects.all().order_by("-name")

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user only"""

        new_user = create_user(email="new_user@example.com")
        Tag.objects.create(user=new_user)
        tag = Tag.objects.create(user=self.user, name="Tag 3")
        response = self.client.get(TAG_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], tag.name)
        self.assertEqual(response.data[0]["id"], tag.id)

    def test_update_tags(self):
        """Test updating a tag"""

        tag = Tag.objects.create(user=self.user, name="Tag example")

        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()

        self.assertEqual(tag.name, payload["name"])

    def test_delete_tags(self):
        """test deleting tag"""

        tag = Tag.objects.create(user=self.user, name="Simple tag")
        url = detail_url(tag_id=tag.id)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test filter tags to those assigned to recipes"""

        tag1 = Tag.objects.create(user=self.user, name="Dinner")
        tag2 = Tag.objects.create(user=self.user, name="Lunch")

        recipe = Recipe.objects.create(
            title="Chicken curry",
            time_minutes=10,
            price=Decimal("19.0"),
            user=self.user,
        )

        recipe.tags.add(tag1)

        response = self.client.get(TAG_URL, {"assigned_only": 1})
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, response.data)
        self.assertNotIn(s2.data, response.data)

    def test_filtered_tags_unique(self):
        """Test filter tags return unique list"""

        tag = Tag.objects.create(user=self.user, name="Desert")
        Tag.objects.create(user=self.user, name="Dinner")

        recipe1 = Recipe.objects.create(
            title="Ice cream",
            time_minutes=19,
            price=Decimal("12"),
            user=self.user,
        )

        recipe2 = Recipe.objects.create(
            title="Cake",
            time_minutes=42,
            price=Decimal("10.3"),
            user=self.user,
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        response = self.client.get(TAG_URL, {"assigned_only": 1})

        self.assertEqual(len(response.data), 1)

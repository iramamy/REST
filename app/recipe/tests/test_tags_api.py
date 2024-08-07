"""Test for the tags API"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


from core.models import Tag
from recipe.serializers import TagSerializer

TAG_URL = reverse("recipe:tag-list")


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

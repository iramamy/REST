"""
Test for models
"""

from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal

from core import models


def create_user(email="user@example.com", password="testpass1234_"):
    """Create and return a new user"""

    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    """Test Model"""

    def test_create_user_with_email_success(self):
        """Test use with an email is successful"""
        email = "test@example.com"
        password = "pa$$word123_"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(
            user.email,
            email,
        )
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test use email is normalized"""
        sample_emails = [
            ["test1@Example.com", "test1@example.com"],
            ["Test2@ExAmpLe.com", "Test2@example.com"],
            ["TesT3@EXAMPLE.com", "TesT3@example.com"],
            ["TEST4@EXAMPLE.com", "TEST4@example.com"],
        ]

        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(
                email,
                "sample123",
            )
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Raises error when user does not provide email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_super_user(self):
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test create recipe is successful"""

        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password123_",
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Simple recipe title",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample test recipe description",
        )

        self.assertEqual(f"{recipe}", recipe.title)

    def test_create_tag(self):
        """Test create tag successful"""

        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(f"{tag}", tag.name)

    def test_create_ingredient(self):
        """Test create ingredient successful"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name="Ingredient1",
        )

        self.assertEqual(ingredient.name, f"{ingredient}")

    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "example.jpeg")

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpeg")

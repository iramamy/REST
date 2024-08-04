"""
Test for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """Test Model"""

    def test_create_user_with_email_success(self):
        """Test use with an email is successful"""
        email = "test@example.com"
        password = "pa$$word123_"
        user = get_user_model().objects.create_user(
            email=email, password=password
        )  # noqa
        self.assertEqual(user.email, email)
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
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Raises error when user does not provide email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_super_user(self):
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser(
            "test@example.com", "test123"
        )  # noqa

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

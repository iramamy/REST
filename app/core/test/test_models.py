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
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
"""
Test for django admin modifications

"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Test for django admin"""

    def setUp(self):
        """Create user and client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com", password="admintest1234_"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="test1234_", name="Test User"  # noqa
        )

    def test_user_list(self):
        """Test that users are listed on page"""
        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_edit_page(self):
        """Test if the user edit page works"""

        url = reverse("admin:core_user_change", args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test if user page works"""

        url = reverse("admin:core_user_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

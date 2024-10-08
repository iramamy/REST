"""Test for the user api"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_USL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    """Create and return new user"""

    return get_user_model().objects.create_user(**params)


class PublicUserAPiTest(TestCase):
    """Test the public features of the user api"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating user is successful"""

        payload = {
            "email": "test@example.com",
            "password": "pa$$word123_",
            "name": "Test User",
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

        self.assertNotIn("password", response.data)

    def test_user_with_email_exists_error(self):
        """Test if user email already exists"""

        payload = {
            "email": "test@example.com",
            "password": "pa$$word123_",
            "name": "Test User",
        }

        create_user(**payload)

        respone = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(respone.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Return error if password is too short while creating user"""

        payload = {
            "email": "test@example.com",
            "password": "pa$$",
            "name": "Test User",
        }

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )  # noqa

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Generated token for user with valid credentials"""

        user_details = {
            "name": "Test name",
            "email": "usertest@example.com",
            "password": "pa$$word123_",
        }

        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }  # noqa

        response = self.client.post(TOKEN_USL, payload)

        self.assertIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if user enter wrong credentials"""

        create_user(
            email="testuser@example.com",
            password="goodpassword",
        )

        payload = {
            "email": "testuser@example.com",
            "password": "wrongpasswrod",
        }

        response = self.client.post(TOKEN_USL, payload)

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Return error if user enter blank password"""

        payload = {
            "email": "testuser@example.com",
            "password": "",
        }

        response = self.client.post(TOKEN_USL, payload)

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for user"""

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API for authenticated user"""

    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            password="testpassword123_",
            name="test name",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_success(self):
        """Test retrieve profile for authenticated user"""

        response = self.client.get(ME_URL)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data,
            {
                "name": self.user.name,
                "email": self.user.email,
            },
        )

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""

        response = self.client.post(ME_URL, {})

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_update_user_profile(self):
        """Update profile for authenticated user"""

        payload = {
            "name": "Updated new name",
            "password": "newpassword",
        }

        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

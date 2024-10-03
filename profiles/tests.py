from django.test import TestCase
from django.contrib.auth import get_user_model

class UserProfileTests(TestCase):
    """Tests for the UserProfile model."""

    def setUp(self):
        self.email = 'testuser@example.com'
        self.password = 'TestPass123'
        self.first_name = 'Test'
        self.last_name = 'User'

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        user = get_user_model().objects.create_user(
            email=self.email,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name
        )
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(user.get_full_name(), f"{self.first_name} {self.last_name}")
        self.assertEqual(user.get_username(), self.email)
        self.assertTrue(user.is_authenticated())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser."""
        user = get_user_model().objects.create_superuser(
            email=self.email,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)
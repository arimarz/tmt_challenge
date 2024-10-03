from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class UserProfileManager(BaseUserManager):
    """Manager for UserProfile."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError('An email address is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        if not extra_fields.get('is_admin'):
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(email, password, **extra_fields)

class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Custom user model that uses email as the username."""

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)  # For admin site access
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)  # Custom admin flag
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def get_username(self):
        """Return the user's email address (used as username)."""
        return self.email

    def is_authenticated(self):
        """Always return True. This is a way to tell if the user has been authenticated."""
        return True

    def __str__(self):
        """Return string representation of the user."""
        return self.email

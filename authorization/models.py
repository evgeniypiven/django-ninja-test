"""
Authorization Models
"""

# Standard library imports.

# Related third party imports.
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models, transaction
from django.core import validators
from django.utils.translation import gettext_lazy as _

# Local application/library specific imports.


class CustomUserManager(BaseUserManager):
    @transaction.atomic
    def _create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required.')

        if not email:
            raise ValueError('Email is required.')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Super user must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Super user must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)

    email = models.EmailField(
        validators=[validators.validate_email],
        unique=True,
        blank=False
    )

    is_staff = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', 'password')

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'authorization'
        db_table = 'django_ninja_test_authorization_custom_user'
        verbose_name = _('Custom User')
        verbose_name_plural = _('Custom Users')

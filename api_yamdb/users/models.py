import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin')
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE,
        default=USER,
    )
    username = models.CharField(
        "Имя пользователя",
        max_length=150,
        unique=True,
        blank=False,
        null=False,
    )
    bio = models.TextField(
        "Биография",
        blank=True,
    )
    email = models.EmailField(
        "email",
        unique=True,
        null=False,
        max_length=254
    )
    first_name = models.CharField(
        "Имя",
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=150,
        blank=True
    )
    confirmation_code = models.UUIDField(default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELDS = "email"

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER

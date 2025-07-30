from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name="Email",
        unique=True,
        blank=False,
        null=False,
    )
    avatar = models.ImageField(
        upload_to="images/avatar/%Y/%m/%d",
        verbose_name="Аватар",
        null=True,
        blank=True,
        max_length=255,
    )

    USERNAME_FIELD: str = "email"
    REQUIRED_FIELDS: list[str] = ["username", "first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.email

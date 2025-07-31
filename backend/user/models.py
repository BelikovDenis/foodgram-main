from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .constants import (
    MAX_EMAIL_FIELD_LENGTH,
    MAX_USERNAME_FIELD_LENGTH,
    MAX_AVATAR_FIELD_LENGTH
)


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        blank=False,
        null=False,
        max_length=MAX_EMAIL_FIELD_LENGTH
    )
    avatar = models.ImageField(
        upload_to='images/avatar/%Y/%m/%d',
        verbose_name='Аватар',
        null=True,
        blank=True,
        max_length=MAX_AVATAR_FIELD_LENGTH,
        default=''
    )
    username = models.CharField(
        max_length=MAX_USERNAME_FIELD_LENGTH,
        unique=True,
        verbose_name='username',
        validators=[UnicodeUsernameValidator()],
        help_text=(
            'Обязательное поле. Не более 150 символов. '
            'Только буквы, цифры и символы @/./+/-/_.'
        ),
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        }
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='subscriptions',
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='followers',
        on_delete=models.CASCADE,
        verbose_name='автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

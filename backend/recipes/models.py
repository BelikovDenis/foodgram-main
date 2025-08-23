import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.constants import (
    COOKING_TIME_MAX,
    COOKING_TIME_MIN,
    INGREDIENT_MAX_AMOUNT,
    INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    INGREDIENT_MIN_AMOUNT,
    INGREDIENT_NAME_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)
from core.validators import validate_image_format

User = get_user_model()


def generate_short_code(length=7):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    short_link = models.CharField(
        max_length=7,
        unique=True,
        blank=True,
        default=generate_short_code
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Имя',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Фото',
        validators=[validate_image_format]
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(COOKING_TIME_MIN),
            MaxValueValidator(COOKING_TIME_MAX)
        ]
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = generate_short_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BaseFavoriteShopping(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(BaseFavoriteShopping):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Рецепт'
    )

    class Meta(BaseFavoriteShopping.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shoppingcart',
            )
        ]
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(INGREDIENT_MIN_AMOUNT),
            MaxValueValidator(INGREDIENT_MAX_AMOUNT)
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} - {self.amount}'


class Favorite(BaseFavoriteShopping):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta(BaseFavoriteShopping.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

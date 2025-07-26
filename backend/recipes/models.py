from django.contrib.auth import get_user_model
from django.db import models

from user.models import CustomUser

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=32, unique=True, verbose_name="Slug")
    color = models.CharField(
        max_length=7,
        verbose_name="Цвет в HEX",
        blank=True,
        null=True,
        default='#ffffff',
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=256,
        verbose_name="Имя",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Фото",
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Тег",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Автор",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_carts",
        verbose_name="Рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_shoppingcart",
            )
        ]
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name="Название ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=32,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_ingredient_in_recipe",
            )
        ]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name="пользователь",
    )
    author = models.ForeignKey(
        CustomUser,
        related_name="followers",
        on_delete=models.CASCADE,
        verbose_name="автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscription"
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="избранное",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite"
            )
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

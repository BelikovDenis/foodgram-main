from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from user.models import Subscription

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cooking_time_in_minutes',
        'author',
        'tag_names',
        'ingredients_summary',
        'favorites_count',
        'image_preview',
    )
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    inlines = (IngredientInRecipeInline,)
    filter_horizontal = ('tags',)
    readonly_fields = ('favorites_count',)
    list_per_page = 20

    @admin.display(description='Время приготовления')
    def cooking_time_in_minutes(self, obj):
        return f'{obj.cooking_time} мин.'

    @admin.display(description='Теги')
    def tag_names(self, obj):
        tags = ', '.join(tag.name for tag in obj.tags.all())
        return tags or '-'

    @admin.display(description='Ингредиенты')
    def ingredients_summary(self, obj):
        ingredients = []
        for ingredient_in_recipe in obj.recipe_ingredients.all():
            ingredient = ingredient_in_recipe.ingredient
            ingredients.append(
                f'{ingredient.name}: '
                f'{ingredient_in_recipe.amount} '
                f'{ingredient.measurement_unit}'
            )
        return mark_safe('<br>'.join(ingredients)) if ingredients else '-'

    @admin.display(description='Картинка')
    def image_preview(self, obj):
        return format_html('<img src="{}" width="50"' \
        'height="50"style="object-fit: cover;"/>', obj.image.url)

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'used_in_recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    list_per_page = 50

    @admin.display(description='Применено в рецептах')
    def used_in_recipes_count(self, obj):
        return obj.ingredientinrecipe_set.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_per_page = 20


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_select_related = ('user', 'recipe')
    list_per_page = 50


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_select_related = ('user', 'recipe')
    list_per_page = 50


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_select_related = ('user', 'author')
    list_per_page = 50

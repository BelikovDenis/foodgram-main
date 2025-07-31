from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)

class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1

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

    def cooking_time_in_minutes(self, obj):
        return f'{obj.cooking_time} мин.'
    cooking_time_in_minutes.short_description = 'Время приготовления'

    def tag_names(self, obj):
        tags = ', '.join(tag.name for tag in obj.tags.all())
        return mark_safe(tags)
    tag_names.short_description = 'Теги'

    def ingredients_summary(self, obj):
        ingredients = '<br>'.join(
            ingredient.name + ': ' + str(amount.amount) +
            ' ' + amount.measurement_unit
            for ingredient, amount in zip(obj.ingredients.all(),
                                          obj.ingredient_amounts.all())
        )
        return mark_safe(ingredients)
    ingredients_summary.short_description = 'Ингредиенты'

    def image_preview(self, obj):
        return format_html('<img src="{}" width="50"/>', obj.image.url)
    image_preview.short_description = 'Картинка'

    def favorites_count(self, obj):
        return obj.favorited_by.count()
    favorites_count.short_description = 'Добавлений в избранное'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'used_in_recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    def used_in_recipes_count(self, obj):
        return obj.recipe_set.count()
    used_in_recipes_count.short_description = 'Применено в рецептах'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
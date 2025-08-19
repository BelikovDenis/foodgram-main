from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

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
    fields = ('ingredient', 'amount', 'get_measurement_unit')
    readonly_fields = ('get_measurement_unit',)

    def get_measurement_unit(self, instance):
        return (instance.ingredient.measurement_unit
                if instance.ingredient else '-')
    get_measurement_unit.short_description = 'Единица измерения'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'cooking_time_in_minutes',
        'tag_names',
        'ingredients_summary',
        'favorites_count',
        'image_preview',
    )
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    inlines = (IngredientInRecipeInline,)
    filter_horizontal = ('tags',)
    readonly_fields = ('favorites_count', 'image_preview')
    list_per_page = 20
    autocomplete_fields = ('author',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'tags', 'recipe_ingredients__ingredient'
        ).select_related('author').annotate(
            favorites_count=Count('favorites')
        )

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
        return format_html('<br>'.join(ingredients)) if ingredients else '-'

    @admin.display(description='Картинка')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="object-fit: cover;"/>',
                obj.image.url
            )
        return '-'

    @admin.display(description='В избранном', ordering='favorites_count')
    def favorites_count(self, obj):
        return obj.favorites_count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'used_in_recipes_count')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_per_page = 50
    ordering = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipe_count=Count('ingredientinrecipe')
        )

    @admin.display(description='Использований', ordering='recipe_count')
    def used_in_recipes_count(self, obj):
        return obj.recipe_count


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_preview')
    search_fields = ('name', 'slug')
    list_per_page = 20
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('color_preview',)

    @admin.display(description='Цвет')
    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; '
                'background-color: {}; border: 1px solid #000;"></div>',
                obj.color
            )
        return '-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_select_related = ('user', 'recipe')
    list_per_page = 50
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_select_related = ('user', 'recipe')
    list_per_page = 50
    search_fields = ('user__username', 'recipe__name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_select_related = ('user', 'author')
    list_per_page = 50
    search_fields = ('user__username', 'author__username')

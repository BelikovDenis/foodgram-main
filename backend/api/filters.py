from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_by_user_relation'
    )
    is_favorited = filters.BooleanFilter(method='filter_by_user_relation')

    def filter_by_user_relation(self, queryset, name, value):
        """
        Фильтрация рецептов по отношениям пользователя.
        """
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset

        field_mapping = {
            'is_in_shopping_cart': 'in_shopping_carts__user',
            'is_favorited': 'favorited_by__user',
        }
        field_name = field_mapping.get(name)

        if not field_name:
            return queryset

        if value:
            return queryset.filter(**{field_name: user})
        return queryset.exclude(**{field_name: user})

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)

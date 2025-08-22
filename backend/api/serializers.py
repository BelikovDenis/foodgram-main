import io

from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from PIL import Image
from rest_framework import serializers

from core.constants import (
    DEFAULT_RECIPES_LIMIT,
    INGREDIENT_MIN_AMOUNT,
    MAX_RECIPES_LIMIT,
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from user.models import CustomUser, Subscription


class CustomUserBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователей."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """
        Проверяет наличие подписки текущего пользователя на автора.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                author=obj,
            ).exists()
        return False


class CustomUserWithRecipesSerializer(CustomUserBaseSerializer):
    """Расширенный сериализатор пользователей с рецептами."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserBaseSerializer.Meta):
        fields = CustomUserBaseSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """
        Возвращает рецепты пользователя согласно лимиту.
        """
        request = self.context.get('request')
        recipes = obj.recipes.order_by('-pub_date')
        limit = DEFAULT_RECIPES_LIMIT

        if request and hasattr(request, 'query_params'):
            limit_param = request.query_params.get('recipes_limit')

            if limit_param is not None:
                try:
                    requested_limit = int(limit_param)
                    if requested_limit < 1:
                        limit = DEFAULT_RECIPES_LIMIT
                    elif requested_limit > MAX_RECIPES_LIMIT:
                        limit = MAX_RECIPES_LIMIT
                    else:
                        limit = requested_limit
                except (TypeError, ValueError):
                    pass

        recipes = recipes[:limit]
        return RecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов пользователя.
        """
        return obj.recipes.count()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователей."""
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagPublicSerializer(serializers.ModelSerializer):
    """Сериализатор публичных данных тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    author = CustomUserWithRecipesSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ('author',)


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения ингредиентов в рецепте."""
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id if obj.ingredient else None

    def get_name(self, obj):
        return obj.ingredient.name if obj.ingredient else None

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit if obj.ingredient else None


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        error_messages={
            'does_not_exist':
                'Ингредиент с указанным id не найден.',
        },
    )
    amount = serializers.IntegerField(min_value=INGREDIENT_MIN_AMOUNT)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов."""
    short_link = serializers.CharField(read_only=True)
    tags = TagPublicSerializer(many=True, read_only=True)
    author = CustomUserBaseSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
            'short_link',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_carts.filter(user=request.user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи рецептов."""
    ingredients = IngredientInRecipeWriteSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        """
        Валидирует ингредиенты на уникальность.
        """
        if not value:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        unique_ingredients = set()
        for item in value:
            ing_id = item['id'].id
            if ing_id in unique_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            unique_ingredients.add(ing_id)
        return value

    def validate_tags(self, value):
        """
        Валидирует теги на уникальность.
        """
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один тег.'
            )
        tag_ids = [tag.id for tag in value]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return value

    def create_ingredients(self, ingredients_data, recipe):
        """
        Создает ингредиенты для рецепта.
        """
        objs = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount'],
            ) for item in ingredients_data
        ]
        IngredientInRecipe.objects.bulk_create(objs)

    def validate_cooking_time(self, value):
        """
        Валидирует минимальное значение времени приготовления.
        """
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше нуля.'
            )
        return value

    def create(self, validated_data):
        """
        Создает новый рецепт.
        """
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.
        """
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)

        instance.recipe_ingredients.all().delete()
        self.create_ingredients(ingredients_data, instance)

        return instance


class Base64ImageField(Base64ImageField):
    ALLOWED_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp', 'heic']

    def get_file_extension(self, filename, decoded_file):
        try:
            image = Image.open(io.BytesIO(decoded_file))
            return image.format.lower()
        except Exception:
            return super().get_file_extension(filename, decoded_file)


class BaseRecipeRelationSerializer(serializers.ModelSerializer):
    """
    Базовый класс для сериализаторов отношений с рецептами.
    """
    def to_representation(self, instance):
        return RecipeMiniSerializer(
            instance.recipe if hasattr(instance, 'recipe') else instance,
            context=self.context,
        ).data

    def validate(self, data):
        user = self.context["request"].user
        recipe = self.context['recipe']
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт уже в {self.Meta.model._meta.verbose_name}.'
            )
        return data


class FavoriteSerializer(BaseRecipeRelationSerializer):
    """Сериализатор избранных рецептов."""
    class Meta:
        model = Favorite
        fields = ()


class ShoppingCartSerializer(BaseRecipeRelationSerializer):
    """Сериализатор списка покупок."""
    class Meta:
        model = ShoppingCart
        fields = ()


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Мини-сериализатор рецептов."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

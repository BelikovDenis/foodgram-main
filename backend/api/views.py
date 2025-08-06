from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import RecipeActionMixin
from api.pagination import CustomLimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CustomUserBaseSerializer,
    CustomUserWithRecipesSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    TagPublicSerializer,
)
from api.utils.utils import (
    generate_csv_content,
    generate_pdf,
    generate_text_content,
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

User = get_user_model()


class RecipeViewSet(RecipeActionMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.order_by('-pub_date').select_related(
        'author'
    ).prefetch_related(
        'tags', 'ingredients'
    )
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    search_fields = ('^name', 'name')
    filterset_class = RecipeFilter
    pagination_class = CustomLimitPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite_add(self, request, pk=None):
        return self.perform_action(
            request=request,
            pk=pk,
            model=Favorite,
            serializer_class=FavoriteSerializer,
            error_message='Рецепт уже в избранном.',
        )

    @favorite_add.mapping.delete
    def favorite_delete(self, request, pk=None):
        return self.favorite_add(request, pk)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart_add(self, request, pk=None):
        return self.perform_action(
            request=request,
            pk=pk,
            model=ShoppingCart,
            serializer_class=ShoppingCartSerializer,
            error_message='Рецепт уже в списке покупок.',
        )

    @shopping_cart_add.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        return self.shopping_cart_add(request, pk)

    @action(
        detail=True,
        methods=['GET'],
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        url = request.build_absolute_uri(f'/recipes/{pk}/')
        return Response({'short-link': url}, status=status.HTTP_200_OK)


def redirect_to_recipe(request, short_code):
    recipe_id = decode_base62(short_code)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return redirect(f"/recipes/{recipe.id}/")


class FavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(
            favorited_by__user=self.request.user,
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = TagPublicSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class ShoppingCartViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(
            in_shopping_carts__user=self.request.user,
        ).order_by("-in_shopping_carts__id")


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "id"
    lookup_field = "id"
    pagination_class = CustomLimitPagination

    def get_serializer_class(self):
        if self.action in ["me", "retrieve"]:
            return CustomUserBaseSerializer
        return super().get_serializer_class()

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="subscribe",
        url_name="subscribe",
    )
    def subscribe(self, request, *args, **kwargs):
        """Подписаться/отписаться на пользователя"""
        author = self.get_object()
        user = request.user
        if user == author:
            return Response(
                {"error": "Нельзя подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "POST":
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {"error": "Вы уже подписаны на этого пользователя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Subscription.objects.create(user=user, author=author)
            serializer = CustomUserWithRecipesSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count, _ = Subscription.objects.filter(
            user=user, author=author
        ).delete()
        if deleted_count == 0:
            return Response(
                {"error": "Вы не подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="subscriptions",
        url_name="subscriptions",
    )
    def subscriptions(self, request):
        """Получить список моих подписок"""
        user = request.user
        authors = CustomUser.objects.filter(followers__user=user)
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = CustomUserWithRecipesSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = CustomUserWithRecipesSerializer(
            authors, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["put", "delete"], url_path="me/avatar")
    def avatar(self, request):
        user = request.user
        if request.method == "PUT":
            serializer = CustomUserBaseSerializer(
                user,
                data={"avatar": request.data.get("avatar")},
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"avatar": user.avatar.url}, status=status.HTTP_200_OK
            )
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class DownloadShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def _prepare_shopping_list_data(self, user):
        qs = IngredientInRecipe.objects.filter(
            recipe__in_shopping_carts__user=user
        )
        if not qs.exists():
            return []
        aggregated = qs.values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit'),
        ).annotate(total=Sum('amount'))
        return [
            {
                'name': item['name'],
                'unit': item['unit'],
                'total': item['total']
            }
            for item in aggregated
        ]

    def _text_response(self, content, filename):
        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _csv_response(self, content, filename):
        response = HttpResponse(
            content,
            content_type='text/csv; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _pdf_response(self, buffer, filename):
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def get(self, request):
        file_format = request.GET.get('format', 'txt').lower()
        data = self._prepare_shopping_list_data(request.user)
        filename = 'shopping_list'

        if file_format == 'pdf':
            buffer = generate_pdf(data)
            return self._pdf_response(buffer, f'{filename}.pdf')
        elif file_format == 'csv':
            content = generate_csv_content(data)
            return self._csv_response(content, f'{filename}.csv')
        else:
            content = generate_text_content(data)
            return self._text_response(content, f'{filename}.txt')

    def post(self, request):
        email = request.data.get('email', request.user.email)
        send_format = request.data.get('format', 'txt').lower()
        data = self._prepare_shopping_list_data(request.user)
        attachments = []
        content = ''

        if send_format == 'pdf':
            buffer = generate_pdf(data)
            attachments.append((
                'shopping_list.pdf',
                buffer.getvalue(),
                'application/pdf'
            ))
            content = 'Ваш список покупок во вложении.'
        elif send_format == 'csv':
            csv_content = generate_csv_content(data)
            attachments.append((
                'shopping_list.csv',
                csv_content,
                'text/csv'
            ))
            content = 'Ваш список покупок во вложении.'
        else:
            text_content = generate_text_content(data)
            attachments.append((
                'shopping_list.txt',
                text_content,
                'text/plain'
            ))
            content = 'Ваш список покупок во вложении.'

        email_msg = EmailMessage(
            subject='Ваш список покупок',
            body=content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        for attachment in attachments:
            email_msg.attach(*attachment)
        email_msg.send()

        return Response(
            {'status': 'Список покупок отправлен на вашу почту'},
            status=status.HTTP_200_OK
        )

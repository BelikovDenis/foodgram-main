from django.contrib.auth import get_user_model
from django.db.models import Count, F, Prefetch, Sum
from django.http import Http404, HttpResponse
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
from django.conf import settings
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from io import BytesIO
import csv

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
from api.utils.base62 import decode_base62
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)
from user.models import CustomUser

User = get_user_model()


class RecipeViewSet(RecipeActionMixin, viewsets.ModelViewSet):

    queryset = Recipe.objects.order_by("-pub_date")
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
        recipe = get_object_or_404(Recipe, pk=pk)
        url = request.build_absolute_uri(f'/recipes/{pk}/')
        return Response({'short-link': url}, status=status.HTTP_200_OK)


class DownloadShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def _prepare_shopping_list_data(self, user):
        """
        Формирует данные списка покупок отдельно от запросов.
        Возвращает агрегированные ингредиенты.
        """
        qs = IngredientInRecipe.objects.filter(recipe__in_shopping_carts__user=user)
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

    def _generate_text_content(self, data):
        """Генерирует текстовое содержимое для списка покупок."""
        lines = [f"{item['name']} ({item['unit']}) — {item['total']}"
                 for item in data]
        return '\n'.join(lines)

    def _generate_csv_content(self, data):
        """Генерирует CSV содержимое для списка покупок."""
        output = []
        writer = csv.writer(output)
        writer.writerow(['Ингредиент', 'Единица измерения', 'Количество'])
        for item in data:
            writer.writerow([item['name'], item['unit'], item['total']])
        return '\n'.join([','.join(map(str, row)) for row in output])

    def _generate_pdf(self, data):
        """Генерирует PDF документ со списком покупок."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title = Paragraph('Список покупок', title_style)
        elements.append(title)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
        if data:
            table_data = [['Ингредиент', 'Единица измерения', 'Количество']]
            for item in data:
                table_data.append([
                    item['name'],
                    item['unit'],
                    str(item['total'])
                ])
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph('Ваш список покупок пуст.',
                                     styles['Normal']))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _text_response(self, content, filename):
        """Возвращает текстовый HTTP ответ."""
        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _csv_response(self, data, filename):
        """Возвращает CSV HTTP ответ."""
        content = self._generate_csv_content(data)
        response = HttpResponse(
            content,
            content_type='text/csv; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _pdf_response(self, buffer, filename):
        """Возвращает PDF HTTP ответ."""
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def get(self, request):
        """Возвращает файл со списком покупок в выбранном формате."""
        file_format = request.GET.get('format', 'txt').lower()
        data = self._prepare_shopping_list_data(request.user)
        filename = 'shopping_list'
        if file_format == 'pdf':
            buffer = self._generate_pdf(data)
            return self._pdf_response(buffer, f'{filename}.pdf')
        elif file_format == 'csv':
            return self._csv_response(data, f'{filename}.csv')
        else:
            content = self._generate_text_content(data)
            return self._text_response(content, f'{filename}.txt')

    def post(self, request):
        """Отправляет список покупок по email."""
        email = request.data.get('email', request.user.email)
        send_format = request.data.get('format', 'txt').lower()
        data = self._prepare_shopping_list_data(request.user)
        filename = 'shopping_list'
        if send_format == 'pdf':
            buffer = self._generate_pdf(data)
            attachments = [
                ('shopping_list.pdf',
                 buffer.getvalue(),
                 'application/pdf')
            ]
            content = 'Ваш список покупок во вложении.'
        elif send_format == 'csv':
            csv_content = self._generate_csv_content(data)
            attachments = [
                ('shopping_list.csv',
                 csv_content,
                 'text/csv')
            ]
            content = 'Ваш список покупок во вложении.'
        else:
            content = self._generate_text_content(data)
            attachments = [
                ('shopping_list.txt',
                 content,
                 'text/plain')
            ]
        email_msg = EmailMessage(
            subject='Ваш список покупок',
            body=content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        if attachments:
            for filename, content, mime_type in attachments:
                email_msg.attach(filename, content, mime_type)
        email_msg.send()
        return Response(
            {'status': 'Список покупок отправлен на вашу почту'},
            status=status.HTTP_200_OK
        )

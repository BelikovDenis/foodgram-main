from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet,
    DownloadShoppingCartView,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register(r"recipes", RecipeViewSet, basename="recipe")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"ingredients", IngredientViewSet, basename="ingredient")
router.register(r"users", CustomUserViewSet, basename="customuser")

urlpatterns = [
    path(
        "recipes/download_shopping_cart/",
        DownloadShoppingCartView.as_view(),
        name="download_shopping_cart",
    ),
    path("", include(router.urls)),
]

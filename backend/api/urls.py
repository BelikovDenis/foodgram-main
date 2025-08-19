from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

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
    path(
        "r/<str:short_code>/",
        views.redirect_to_recipe,
        name="redirect_to_recipe",
    ),
    path("", include(router.urls)),
]

from django.urls import include, path
from django.contrib import admin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
]

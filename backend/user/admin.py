from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'get_recipes_count',
        'get_subscribers_count'
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    get_recipes_count.short_description = 'Рецепты'

    def get_subscribers_count(self, obj):
        return obj.followers.count()
    get_subscribers_count.short_description = 'Подписчики'


admin.site.unregister(Group)
#  admin.site.unregister(TokenProxy)

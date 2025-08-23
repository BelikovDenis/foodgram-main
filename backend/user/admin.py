from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

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

    @admin.display(description='Рецепты')
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Подписчики')
    def get_subscribers_count(self, obj):
        return obj.followers.count()


admin.site.unregister(Group)

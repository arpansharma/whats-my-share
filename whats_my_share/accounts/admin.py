from django.contrib import admin

# app level imports
from .models import User, Group


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        # 'username',
        # 'first_name',
        # 'last_name',
        # 'email',
    )

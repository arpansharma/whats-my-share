# django/rest-framework imports
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
        'created_at',
        'updated_at',
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'owner',
        'get_members',
        'created_at',
        'updated_at',
    )

    def get_members(self, obj):
        return ", ".join([user.username for user in obj.members.all()])

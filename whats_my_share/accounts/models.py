# django/rest-framework imports
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    profile_picure = models.URLField(max_length=512, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.username}'

    class Meta:
        app_label = 'accounts'
        db_table = 'api_user'
        verbose_name_plural = 'Users'


class Group(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey('accounts.user', related_name="owner_user", on_delete=models.PROTECT)
    members = models.ManyToManyField('accounts.User', related_name='members_users')
    profile_picure = models.URLField(max_length=512, null=True, default=None)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        app_label = 'accounts'
        db_table = 'api_group'
        verbose_name_plural = 'Groups'

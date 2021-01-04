# django/rest-framework imports
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

# project level imports
from accounts import views as user_views
from expense import views as expense_views

# Registering a simple router
router = SimpleRouter()

# Adding endpoints for the app accounts
router.register(r'accounts/user', user_views.UserViewSet, basename='accounts')
router.register(r'accounts/group', user_views.GroupViewSet, basename='accounts')

# Addin endpoints for the app expense
router.register(r'expense', expense_views.ExpenseViewSet, basename='expense')

# Generating url patterns for apps and the django-admin
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('admin/', admin.site.urls),
]

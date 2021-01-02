# django / rest-framework imports
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

# project level imports
from accounts import views as user_views

router = SimpleRouter()
router.register(r'accounts/user', user_views.UserViewSet, basename='accounts')
router.register(r'accounts/group', user_views.GroupViewSet, basename='accounts')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('admin/', admin.site.urls),
]

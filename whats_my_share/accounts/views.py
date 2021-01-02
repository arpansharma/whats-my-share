# django/rest-framework imports
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

# app level imports
from .serializers import (
    RegisterSerializer,
    AuthenticateSerializer,
)
from .services import UserService


class UserViewSet(GenericViewSet):

    http_method_names = ['post']
    serializers = {
        "register": RegisterSerializer,
        "authenticate": AuthenticateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers[self.action]

    @action(methods=['POST'], detail=False, url_path='register')
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response('', status.HTTP_400_BAD_REQUEST)

        UserService.register_user(validated_data=serializer.validated_data)

        return Response('User has been registered')

    @action(methods=['POST'], detail=False, url_path='authenticate')
    def authenticate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response('', status.HTTP_400_BAD_REQUEST)

        auth_token = UserService.authenticate_user(validated_data=serializer.validated_data)

        if auth_token is None:
            return Response('Sorry ! You are not authenticated', status.HTTP_400_BAD_REQUEST)

        return Response({
            'auth_token': auth_token,
        })

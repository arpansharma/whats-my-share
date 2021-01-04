# django/rest-framework imports
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


# app level imports
from .serializers import (
    RegisterSerializer,
    AuthenticateSerializer,
    CreateSerializer,
    AddMemberSerializer,
    RemoveMemberSerializer,
)
from .services import UserService, GroupService


class UserViewSet(GenericViewSet):
    """
    This class represents the ViewSet for User model
    """

    http_method_names = ['post']
    serializers = {
        "register": RegisterSerializer,
        "authenticate": AuthenticateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers[self.action]

    @transaction.atomic
    @action(methods=['POST'], detail=False, url_path='register')
    def register(self, request, *args, **kwargs):
        """
        API to Register a new user
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            raise ParseError(serializer.errors)

        UserService.register_user(validated_data=serializer.validated_data)

        return Response({
            'message': 'User has been registered successfully.',
        })

    @action(methods=['POST'], detail=False, url_path='authenticate')
    def authenticate(self, request, *args, **kwargs):
        """
        API to authenticate a user
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            raise ParseError(serializer.errors)

        auth_token = UserService.authenticate_user(validated_data=serializer.validated_data)

        """
        Returning auth_token in response that
        has to be used for all future requests
        """
        return Response({
            'Token': auth_token,
        })


class GroupViewSet(GenericViewSet):
    """
    This class represents the ViewSet for Group model
    """

    http_method_names = ['post']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializers = {
        "create": CreateSerializer,
        "add_members": AddMemberSerializer,
        "remove_members": RemoveMemberSerializer,
    }

    def get_serializer_class(self):
        return self.serializers[self.action]

    @transaction.atomic
    def create(self, request, *args, **kawrgs):
        """
        API to create a group
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            raise ParseError(serializer.errors)

        serializer.validated_data['owner'] = request.user
        GroupService.create_group(validated_data=serializer.validated_data)

        return Response({
            'message': 'Group has been created successfully.',
        })

    @transaction.atomic
    @action(methods=['POST'], detail=False, url_path='add-members')
    def add_members(self, request, *args, **kwargs):
        """
        API to add members to a group
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            raise ParseError(serializer.errors)

        serializer.validated_data['owner'] = request.user
        GroupService.add_members(validated_data=serializer.validated_data)

        return Response({
            'message': 'Member(s) have been added successfully.',
        })

    @transaction.atomic
    @action(methods=['POST'], detail=False, url_path='remove-members')
    def remove_members(self, request, *args, **kwargs):
        """
        API to remove members from a group
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            raise ParseError(serializer.errors)

        serializer.validated_data['owner'] = request.user
        GroupService.remove_members(validated_data=serializer.validated_data)

        return Response({
            'message': 'Member(s) have been removed successfully.',
        })

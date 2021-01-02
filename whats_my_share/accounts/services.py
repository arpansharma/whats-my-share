# django / rest-framework imports
from rest_framework.exceptions import ParseError
from rest_framework.authtoken.models import Token

# app level imports
from .models import User, Group
from .constants import (
    INCORRECT_PASSWORD,
    INCORRECT_USERNAME,
    GROUP_ALREADY_EXISTS,
    GROUP_DOES_NOT_EXISTS,
)


class UserService:
    def generate_token(user):
        Token.objects.create(user=user)

    def retrieve_token(username, password):
        user = User.objects.filter(username=username).last()
        if user:
            if user.check_password(password):
                auth_token = Token.objects.filter(user__username=username)
                return auth_token.last().key

            raise ParseError(INCORRECT_PASSWORD)
        raise ParseError(INCORRECT_USERNAME)

    def register_user(validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        UserService.generate_token(user=user)

        return user

    def authenticate_user(validated_data):
        username = validated_data['username']
        password = validated_data['password']

        auth_token = UserService.retrieve_token(username=username, password=password)
        return auth_token


class GroupService:
    def create_group(validated_data):
        name = validated_data['name']
        owner = validated_data['owner']

        if Group.objects.filter(name=name).exists():
            raise ParseError(GROUP_ALREADY_EXISTS)

        Group.objects.create(name=name, owner=owner)

    def add_members(validated_data):
        name = validated_data['name']
        owner = validated_data['owner']
        member_usernames = validated_data['members']

        if not Group.objects.filter(name=name).exists():
            raise ParseError(GROUP_DOES_NOT_EXISTS)

        new_members = User.objects.filter(username__in=member_usernames)
        if new_members.count() != len(member_usernames):
            raise ParseError(INCORRECT_USERNAME)

        group = Group.objects.get(name=name, owner=owner)
        group.members.add(*new_members)

    def remove_members(validated_data):
        name = validated_data['name']
        owner = validated_data['owner']
        member_usernames = validated_data['members']

        if not Group.objects.filter(name=name).exists():
            raise ParseError(GROUP_DOES_NOT_EXISTS)

        remove_members = User.objects.filter(username__in=member_usernames)
        if remove_members.count() != len(member_usernames):
            raise ParseError(INCORRECT_USERNAME)

        group = Group.objects.get(name=name, owner=owner)
        group.members.remove(*remove_members)

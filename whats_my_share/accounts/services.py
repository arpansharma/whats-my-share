# django / rest-framework imports
from rest_framework.exceptions import ParseError
from rest_framework.authtoken.models import Token

# app level imports
from .models import User, Group
from .constants import (
    INCORRECT_PASSWORD,
    USERNAME_DOES_NOT_EXIST,
    USERNAME_ALREADY_EXISTS,
    GROUP_ALREADY_EXISTS,
    GROUP_DOES_NOT_EXISTS,
    MEMBERS_NOT_IN_GROUP,
)


class UserService:
    def validate_usernames(usernames):
        users = User.objects.filter(username__in=usernames)

        if users.count() != len(usernames):
            raise ParseError(USERNAME_DOES_NOT_EXIST)

        return users

    def verify_for_existance(username):
        if User.objects.filter(username=username).exists():
            raise ParseError(USERNAME_ALREADY_EXISTS)

    def retrieve_user_objects(usernames):
        return UserService.validate_usernames(usernames=usernames)

    def generate_token(user):
        Token.objects.create(user=user)

    def retrieve_token(username, password):
        user = User.objects.filter(username=username).last()
        if user:
            if user.check_password(password):
                auth_token = Token.objects.filter(user__username=username)
                return auth_token.last().key

            raise ParseError(INCORRECT_PASSWORD)
        raise ParseError(USERNAME_DOES_NOT_EXIST)

    def register_user(validated_data):
        UserService.verify_for_existance(username=validated_data['username'])

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
    def validate_group(name):
        group = Group.objects.filter(name=name).last()

        if group is None:
            raise ParseError(GROUP_DOES_NOT_EXISTS)
        return group

    def verify_for_existance(name):
        if Group.objects.filter(name=name).exists():
            raise ParseError(GROUP_ALREADY_EXISTS)

    def verify_members_in_group(name, members):
        if not Group.objects.filter(name=name, members__in=members).exists():
            raise ParseError(MEMBERS_NOT_IN_GROUP)

    def retrieve_group_object(name):
        return GroupService.validate_group(name=name)

    def create_group(validated_data):
        name = validated_data['name']
        owner = validated_data['owner']

        GroupService.verify_for_existance(name=name)
        Group.objects.create(name=name, owner=owner)

    def add_members(validated_data):
        name = validated_data['name']
        owner = validated_data['owner']
        member_usernames = validated_data['members']

        group = GroupService.validate_group(name=name)
        if group.owner != owner:
            raise ParseError()

        new_members = UserService.validate_usernames(member_usernames)
        group.members.add(*new_members)

    def remove_members(validated_data):
        name = validated_data['name']
        owner = validated_data['owner']
        member_usernames = validated_data['members']

        group = GroupService.validate_group(name=name)
        if group.owner != owner:
            raise ParseError()

        remove_members = UserService.validate_usernames(member_usernames)
        group.members.remove(*remove_members)

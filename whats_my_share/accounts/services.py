# django / rest-framework imports
from rest_framework.authtoken.models import Token

# app level imports
from .models import User


class UserService:
    def generate_token(user):
        Token.objects.create(user=user)

    def retrieve_token(username):
        auth_token = Token.objects.filter(user__username=username)
        if auth_token is None:
            return None

        return auth_token.last().key

    def register_user(validated_data):
        user = User.objects.create(
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
        auth_token = UserService.retrieve_token(username=username)
        return auth_token

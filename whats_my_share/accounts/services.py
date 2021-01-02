# django / rest-framework imports
from rest_framework.authtoken.models import Token

# app level imports
from .models import User


class UserService:
    def generate_token(user):
        Token.objects.create(user=user)

    def retrieve_token(username, password):
        user = User.objects.filter(username=username).last()
        if user:
            if user.check_password(password):
                auth_token = Token.objects.filter(user__username=username)
                return auth_token.last().key

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

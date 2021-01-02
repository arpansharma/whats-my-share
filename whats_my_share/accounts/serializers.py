# django/rest_framework imports
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    """
    This will validate the data required to register a new user.
    """

    username = serializers.CharField(max_length=150, allow_null=False, allow_blank=False)
    first_name = serializers.CharField(max_length=150, allow_null=False, allow_blank=False)
    last_name = serializers.CharField(max_length=150, allow_null=False, allow_blank=False)
    email = serializers.EmailField(allow_null=False, allow_blank=False)
    password = serializers.CharField(max_length=128, allow_null=False, allow_blank=False)
    # retype_password = serializers.CharField(max_length=128, allow_null=False, allow_blank=False)


class AuthenticateSerializer(serializers.Serializer):
    """
    This will validate the data required to authenticate a user.
    """
    username = serializers.CharField(max_length=150, allow_null=False, allow_blank=False)
    password = serializers.CharField(max_length=128, allow_null=False, allow_blank=False)


class CreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64, allow_null=False, allow_blank=False)


class AddMemberSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64, allow_null=False, allow_blank=False)
    members = serializers.ListField(
        child=serializers.CharField(max_length=150, allow_null=False, allow_blank=False),
        allow_empty=False,
        min_length=1,
    )


class RemoveMemberSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64, allow_null=False, allow_blank=False)
    members = serializers.ListField(
        child=serializers.CharField(max_length=150, allow_null=False, allow_blank=False),
        allow_empty=False,
        min_length=1,
    )

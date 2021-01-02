# django/rest_framework imports
from rest_framework import serializers


class CreateSerializer(serializers.Serializer):
    """
    This will validate the data required to add a new expense
    """

    title = serializers.CharField(max_length=64, allow_null=False, allow_blank=False)
    amount = serializers.DecimalField(max_digits=11, decimal_places=2)
    paid_by = serializers.CharField(max_length=150, allow_null=False, allow_blank=False)
    splitting_category = serializers.CharField(max_length=16, allow_null=False, allow_blank=False)
    shared_with_users = serializers.ListField(
        child=serializers.CharField(
            max_length=150, allow_null=False, allow_blank=False,
        ),
        allow_empty=False,
        min_length=1,
        required=False,
    )
    pre_defined_split = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(
                max_length=150, allow_null=False, allow_blank=False,
            ),
            allow_empty=False,
        ),
        allow_empty=False,
        min_length=1,
        required=False,
    )

    group = serializers.CharField(max_length=64, allow_null=False, allow_blank=False)
    notes = serializers.CharField(max_length=1024, required=False, allow_null=False, allow_blank=False)
    comments = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=False)

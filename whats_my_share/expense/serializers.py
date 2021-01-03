# django/rest_framework imports
from rest_framework import serializers


class CreateSerializer(serializers.Serializer):
    """
    This will validate the data required to add a new expense in a group
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

    group_name = serializers.CharField(max_length=64, allow_null=False, allow_blank=False)
    notes = serializers.CharField(max_length=1024, required=False, allow_null=False, allow_blank=False)
    comments = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=False)

    def validate(self, data):
        title = data['title']
        amount = data['amount']
        paid_by = data['paid_by']
        splitting_category = data['splitting_category']
        shared_with_users = data.get('shared_with_users', [])
        pre_defined_split = data.get('pre_defined_split', [])
        group_name = data['group_name']
        notes = data.get('notes', None)
        comments = data.get('comments', None)

        return {
            'title': title,
            'amount': amount,
            'paid_by': paid_by,
            'splitting_category': splitting_category,
            'shared_with_users': shared_with_users,
            'pre_defined_split': pre_defined_split,
            'group_name': group_name,
            'notes': notes,
            'comments': comments,
        }


class SettleBalanceSerializer(serializers.Serializer):
    """
    This will validate the data required to settle balance with a user
    """
    settled_by = serializers.CharField(max_length=150, allow_null=False, allow_blank=False)
    paying_to = serializers.CharField(max_length=150, allow_null=False, allow_blank=False)
    amount = serializers.DecimalField(max_digits=11, decimal_places=2)
    group_name = serializers.CharField(max_length=64, allow_null=False, allow_blank=False)


class FetchBalanceSerializer(serializers.Serializer):
    """
    This will validate the data required to fetch balance for a group
    """
    group_name = serializers.CharField(max_length=64, allow_null=False, allow_blank=False, required=False)

    def validate(self, data):
        group_name = data.get('group_name', None)

        return {
            'group_name': group_name,
        }

# django / rest-framework imports

# project level imports
from account.services import GroupService

# app level imports
from .models import Expense
from .helpers import (
    validate_equally_distributed_expense,
    validate_unequally_distributed_expense,
)


class ExpenseService:
    def add_an_expense(validated_data):
        group_name = validated_data['group']
        splitting_category = validated_data['splitting_category']

        # We need to check if group is already created
        GroupService.validate_group(name=group_name)

        if splitting_category == Expense.SPLITTING_CATEGORY_CHOICES.equally:
            ExpenseService.add_equally_distributed_expense(validated_data=validated_data)
        elif splitting_category in [
            Expense.SPLITTING_CATEGORY_CHOICES.by_percentage,
            Expense.SPLITTING_CATEGORY_CHOICES.by_amount,
        ]:
            ExpenseService.add_unequally_distributed_expense(validated_data=validated_data)

    def add_equally_distributed_expense(validated_data):
        username_share_mapping = validate_equally_distributed_expense(
            validated_data=validated_data,
        )

        return username_share_mapping

    def add_unequally_distributed_expense(validated_data):
        username_share_mapping = validate_unequally_distributed_expense(
            validated_data=validated_data,
        )

        return username_share_mapping

# django / rest-framework imports

# project level imports
from accounts.services import UserService, GroupService

# app level imports
from .models import Expense, LedgerTimeline
from .helpers import (
    validate_equally_distributed_expense,
    validate_unequally_distributed_expense,
    create_ledger_timeline,
)


class ExpenseService:
    def add_an_expense(validated_data, user):
        group_name = validated_data['group']
        splitting_category = validated_data['splitting_category']

        # We need to check if the group exists
        GroupService.validate_group(name=group_name)

        if splitting_category == Expense.equally:
            ExpenseService.add_equally_distributed_expense(
                validated_data=validated_data,
                user=user,
            )
        elif splitting_category in [
            Expense.by_percentage,
            Expense.by_amount,
        ]:
            ExpenseService.add_unequally_distributed_expense(
                validated_data=validated_data,
                user=user,
            )

    def add_equally_distributed_expense(validated_data, user):
        username_share_mapping = validate_equally_distributed_expense(
            validated_data=validated_data,
        )

        expense = ExpenseService.create_expense(
            validated_data=validated_data,
            username_share_mapping=username_share_mapping,
        )

        create_ledger_timeline(
            expense=expense,
            username_share_mapping=username_share_mapping,
            event=LedgerTimeline.expense,
            user=user,
        )

        return username_share_mapping

    def add_unequally_distributed_expense(validated_data, user):
        username_share_mapping = validate_unequally_distributed_expense(
            validated_data=validated_data,
        )

        return username_share_mapping

    def create_expense(validated_data, username_share_mapping):
        """
        """
        paid_by = UserService.retrieve_user_objects(
            usernames=list(validated_data['paid_by']),
        ).last()
        shared_with_users = UserService.retrieve_user_objects(
            usernames=list(username_share_mapping.keys()),
        )
        group = GroupService.retrieve_group_object(name=validated_data['name'])

        expense = Expense.objects.create(
            title=validated_data['title'],
            amount=validated_data['amount'],
            paid_by=paid_by,
            splitting_category=validated_data['splitting_category'],
            shared_with_users=shared_with_users,
            group=group,
            notes=validated_data['notes'],
            comments=validated_data['comments'],
        )

        return expense

# django / rest-framework imports

# project level imports
from accounts.services import UserService, GroupService

# app level imports
from .models import Expense, LedgerTimeline
from .helpers import (
    validate_equally_dist_expense,
    validate_unequally_dist_expense,
)


class ExpenseService:
    def add_an_expense(validated_data, user):
        group_name = validated_data['group']
        splitting_category = validated_data['splitting_category']

        # We need to check if the group exists
        GroupService.validate_group(name=group_name)

        if splitting_category == Expense.EQUALLY:
            username_share_mapping = ExpenseService.add_equally_dist_expense(
                validated_data=validated_data, user=user,
            )
        elif splitting_category in [
            Expense.BY_PERCENTAGE,
            Expense.BY_AMOUNT,
        ]:
            username_share_mapping = ExpenseService.add_unequally_dist_expense(
                validated_data=validated_data, user=user,
            )

        ExpenseService.create_expense(
            validated_data=validated_data,
            username_share_mapping=username_share_mapping,
            user=user,

        )

    def add_equally_dist_expense(validated_data, user):
        username_share_mapping = validate_equally_dist_expense(
            validated_data=validated_data,
        )

        return username_share_mapping

    def add_unequally_dist_expense(validated_data, user):
        username_share_mapping = validate_unequally_dist_expense(
            validated_data=validated_data,
        )

        return username_share_mapping

    def create_expense(validated_data, username_share_mapping, user):
        """
        """
        paid_by = UserService.retrieve_user_objects(
            usernames=[validated_data['paid_by']],
        ).last()
        shared_with_users = UserService.retrieve_user_objects(
            usernames=list(username_share_mapping.keys()),
        )
        group = GroupService.retrieve_group_object(name=validated_data['group'])

        expense = Expense.objects.create(
            title=validated_data['title'],
            amount=validated_data['amount'],
            paid_by=paid_by,
            splitting_category=validated_data['splitting_category'],
            group=group,
            notes=validated_data['notes'],
            comments=validated_data['comments'],
            created_by=user,
        )

        expense.shared_with_users.add(*shared_with_users)

        ExpenseService.add_expense_in_ledger(
            expense=expense, username_share_mapping=username_share_mapping,
        )

        return expense

    def add_expense_in_ledger(expense, username_share_mapping):
        for username, split in username_share_mapping.items():
            debit_from = UserService.retrieve_user_objects(usernames=[username]).last()
            amount = split

            LedgerTimeline.objects.create(
                event=LedgerTimeline.EXPENSE,
                credit_to=expense.paid_by,
                debit_from=debit_from,
                amount=amount,
                expense=expense,
                group=expense.group,
                created_by=expense.created_by,
            )

    def add_settlement_in_ledger(validated_data, user):
        settled_by_username = validated_data['settled_by']
        paying_to_username = validated_data['paying_to']
        amount = validated_data['amount']

        settled_by = UserService.retrieve_user_objects([settled_by_username]).last()
        paying_to = UserService.retrieve_user_objects([paying_to_username]).last()

        LedgerTimeline.objects.create(
            event=LedgerTimeline.SETTLEMENT,
            credit_to=paying_to,
            debit_from=settled_by,
            amount=amount,
            expense=None,
            group=None,
            created_by=user,
        )

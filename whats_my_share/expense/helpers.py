# django/rest-framework imports
from rest_framework.exceptions import ParseError

# project level imports
from accounts.services import UserService

# app level imports
from .models import Expense, LedgerTimeline


def validate_equally_distributed_expense(validated_data):
    """
    This is a helper method that checks the data provided for
    an equally distributed expense and returns username_share_mapping

    """

    amount = validated_data['amount']
    paid_by = validated_data['paid_by']
    shared_with_users = validated_data['shared_with_users']

    # We need to check if usernames provided are registered
    shared_with_users = UserService.validate_usernames(usernames=shared_with_users + paid_by)
    split = round((amount / shared_with_users.count()), 2)

    username_share_mapping = {user.username: split for user in shared_with_users}

    return username_share_mapping


def validate_unequally_distributed_expense(validated_data):
    """
    This is a helper method that checks the data provided for
    an unequally distributed expense and returns username_share_mapping

    """

    amount = validated_data['amount']
    paid_by = validated_data['paid_by']
    splitting_category = validated_data['splitting_category']
    pre_defined_split = validated_data['pre_defined_split']

    if splitting_category == Expense.SPLITTING_CATEGORY_CHOICES.by_percentage:
        username_share_mapping = {}
        for user in pre_defined_split:
            split_value = round(
                (amount * (int(user['split']) / 100)), 2,
            )

            username_share_mapping[user['username']] = split_value

    if splitting_category == Expense.SPLITTING_CATEGORY_CHOICES.by_amount:
        username_share_mapping = {
            user['username']: user['split'] for user in pre_defined_split
        }

    usernames = [paid_by.username]
    total_share = 0
    for username, share in username_share_mapping.items():
        usernames.append(username)
        total_share += share

    # We need to check if usernames provided are registered
    UserService.validate_usernames(usernames=usernames)

    # We need to check if share of all people equals bill amount
    if total_share < amount:
        raise ParseError()

    return username_share_mapping


def create_ledger_timeline(expense, username_share_mapping, event, user):

    for username, split in username_share_mapping.keys():
        debit_from = UserService.retrieve_user_objects(usernames=list(username)).last()
        amount = split

        LedgerTimeline.objects.create(
            event=event,
            credit_to=user,
            debit_from=debit_from,
            amount=amount,
            expense=expense,
            created_by=user,
        )

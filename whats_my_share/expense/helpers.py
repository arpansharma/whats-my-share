# python imports
from decimal import Decimal

# django/rest-framework imports
from rest_framework.exceptions import ParseError

# project level imports
from accounts.services import UserService, GroupService

# app level imports
from .models import Expense
from .constants import INVALID_EXPENSE_TOTAL


def validate_equally_dist_expense(validated_data):
    """
    This is a helper method that checks the data values provided for
    an equally distributed expense and returns username_share_mapping

    username_share_mapping is a dictionary that represents how
    much money is owed by people involved in a expense

    """
    amount = validated_data['amount']
    shared_with_users = validated_data['shared_with_users']
    group_name = validated_data['group_name']

    # We need to check if usernames provided are registered
    shared_with_users = UserService.validate_usernames(usernames=shared_with_users)

    # We need to check if usernames are part of the group
    GroupService.verify_members_in_group(name=group_name, members=shared_with_users)

    # Calculating split for each user
    split = round((amount / shared_with_users.count()), 2)

    username_share_mapping = {user.username: split for user in shared_with_users}

    return username_share_mapping


def validate_unequally_dist_expense(validated_data):
    """
    This is a helper method that checks the data provided for
    an unequally distributed expense and returns username_share_mapping

    username_share_mapping is a dictionary that represents how
    much money is owed by people involved in a expense

    """

    amount = validated_data['amount']
    splitting_category = validated_data['splitting_category']
    pre_defined_split = validated_data['pre_defined_split']

    # Individual share need to be calculated if split is provided in percentage
    if splitting_category == Expense.BY_PERCENTAGE:
        username_share_mapping = {}
        for user in pre_defined_split:
            split_value = round(
                (amount * Decimal((int(user['split']) / 100))), 2,
            )

            username_share_mapping[user['username']] = split_value

    if splitting_category == Expense.BY_AMOUNT:
        username_share_mapping = {
            user['username']: user['split'] for user in pre_defined_split
        }

    usernames = []
    total_share = 0
    for username, share in username_share_mapping.items():
        usernames.append(username)
        total_share += round(float(share), 2)

    # We need to check if usernames provided are registered
    UserService.validate_usernames(usernames=usernames)

    """
    We need to check if share for all people equals bill amount.
    If absolute difference between total_share and amount is greater than 1,
    it will indicate that individual shares provided are not valid.
    """
    if abs(Decimal(total_share) - amount) > 1:
        raise ParseError(INVALID_EXPENSE_TOTAL)

    return username_share_mapping

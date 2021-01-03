# django/rest-framework imports
from rest_framework.exceptions import ParseError

# project level imports
from accounts.services import UserService, GroupService

# app level imports
from .models import Expense


def validate_equally_dist_expense(validated_data):
    """
    This is a helper method that checks the data provided for
    an equally distributed expense and returns username_share_mapping

    """
    amount = validated_data['amount']
    shared_with_users = validated_data['shared_with_users']
    group = validated_data['group']

    # We need to check if usernames provided are registered
    shared_with_users = UserService.validate_usernames(usernames=shared_with_users)

    # We need to check if usernames are part of the group
    GroupService.verify_members_in_group(name=group, members=shared_with_users)

    split = round((amount / shared_with_users.count()), 2)

    username_share_mapping = {user.username: split for user in shared_with_users}

    return username_share_mapping


def validate_unequally_dist_expense(validated_data):
    """
    This is a helper method that checks the data provided for
    an unequally distributed expense and returns username_share_mapping

    """

    amount = validated_data['amount']
    splitting_category = validated_data['splitting_category']
    pre_defined_split = validated_data['pre_defined_split']

    if splitting_category == Expense.BY_PERCENTAGE:
        username_share_mapping = {}
        for user in pre_defined_split:
            split_value = round(
                (amount * (int(user['split']) / 100)), 2,
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
        total_share += share

    # We need to check if usernames provided are registered
    UserService.validate_usernames(usernames=usernames)

    # We need to check if share of all people equals bill amount
    if total_share < amount:
        raise ParseError()

    return username_share_mapping

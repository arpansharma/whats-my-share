# django/rest-framework imports
from rest_framework.exceptions import ParseError

# project level imports
from accounts.services import UserService

# app level imports
from .models import Expense


def validate_data_values(validated_data):
    """
    This is a helper method that checks the data provided for adding an expense.

    1. If expense is equally shared:
        We need to check if usernames provided are registered

    2. If expense is unequally shared:
        We need to check if usernames provided are registered
        We need to check share of all people equals bill amount
    """
    amount = validated_data['amount']
    paid_by = validated_data['paid_by']
    splitting_category = validated_data['splitting_category']
    shared_with_users = validated_data['shared_with_users']
    pre_defined_split = validated_data['pre_defined_split']

    # Checking if the user who has paid the bill is a registered user
    paid_by = UserService.validate_usernames(usernames=list(paid_by))

    # Checks invloved if the expense is equally distributed
    if splitting_category == Expense.SPLITTING_CATEGORY_CHOICES.equally:
        # Checking for existance of data
        if len(shared_with_users) == 0:
            raise ParseError()
        else:
            # Checking if shared_with_users contain registered usernames
            shared_with_users = UserService.validate_usernames(usernames=shared_with_users)

    # Checks invloved if the expense is unequally distributed
    if splitting_category in [
        Expense.SPLITTING_CATEGORY_CHOICES.by_percentage,
        Expense.SPLITTING_CATEGORY_CHOICES.by_amount,
    ]:
        # Checking for existance of data
        if len(pre_defined_split) == 0:
            raise ParseError()
        else:
            username_share_mapping = {
                user['username']: user['split'] for user in pre_defined_split
            }

            usernames = []
            total_share = 0
            for username, share in username_share_mapping.items():
                usernames.append(username)
                total_share += share

            # Checking if shared_with_users contain registered usernames
            shared_with_users = UserService.validate_usernames(usernames=usernames)

            # Checking if share of all people equals bill amount
            if total_share != amount:
                raise ParseError()

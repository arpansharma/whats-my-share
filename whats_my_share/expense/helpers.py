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


def construct_netbalance(all_transactions):
    """
    This helper method first constructs a mapping of each user
    along with the credits and debits and then calculates the
    net balance by subtracting debits from the credits of a user

    """
    username_credit_debts_mapping = {}

    for transaction in all_transactions:
        creditor = transaction.credit_to
        debitor = transaction.debit_from
        amount = transaction.amount

        # Mapping all credits
        if username_credit_debts_mapping.get(creditor.username) is None:
            username_credit_debts_mapping[creditor.username] = {}
        if username_credit_debts_mapping[creditor.username].get('credit') is None:
            username_credit_debts_mapping[creditor.username]['credit'] = 0
        username_credit_debts_mapping[creditor.username]['credit'] += amount

        # Mapping all debits
        if username_credit_debts_mapping.get(debitor.username) is None:
            username_credit_debts_mapping[debitor.username] = {}
        if username_credit_debts_mapping[debitor.username].get('debit') is None:
            username_credit_debts_mapping[debitor.username]['debit'] = 0
        username_credit_debts_mapping[debitor.username]['debit'] += amount

    # Calculating net_balance for all usernames
    net_balance = {
        user: (txns.get('credit', 0) - txns.get('debit', 0))
        for user, txns in username_credit_debts_mapping.items()
    }

    return net_balance


def simplify_debts(net_balance):
    """
    This helper method implements the Shortest Path Algorithm
    in context of minimizing CashFlow/Transactions in a group

    net_balance is a mapping of username: total_credits - total_debits
    """
    username_share_mapping = []

    # usernames with max credit and debit
    max_creditor = max(net_balance.values())
    max_debtor = min(net_balance.values())

    # lists in order to provide reverse access to keys of net_balance
    usernames = list(net_balance.keys())
    amount = list(net_balance.values())

    # This condition is required because you cannot simplify with yourself
    if (max_creditor != max_debtor):
        creditor = usernames[amount.index(max_creditor)]
        debtor = usernames[amount.index(max_debtor)]

        result = max_creditor + max_debtor
        if result >= 0:
            print(f"{debtor} needs to pay {creditor} : {round(abs(max_debtor), 2)}")
            username_share_mapping.append({
                'credit_to': creditor,
                'debit_from': debtor,
                'amount': round(abs(max_debtor), 2),
            })

            net_balance.pop(creditor)
            net_balance.pop(debtor)
            net_balance[creditor] = result

            # Settling the debtor
            net_balance[debtor] = 0
        else:
            print(f"{debtor} needs to pay {creditor} : {round(abs(max_debtor), 2)}")
            username_share_mapping.append({
                'credit_to': creditor,
                'debit_from': debtor,
                'amount': round(abs(max_debtor), 2),
            })

            net_balance.pop(creditor)
            net_balance.pop(debtor)

            # Settling the creditor
            net_balance[creditor] = 0
            net_balance[debtor] = result

        simplify_debts(net_balance)

    return username_share_mapping

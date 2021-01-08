# python imports
from decimal import Decimal

# django/rest-framework imports
from django.db.models import Sum
from rest_framework.exceptions import ParseError

# project level imports
from accounts.services import UserService, GroupService

# app level imports
from .models import Expense, LedgerTimeline, Ledger
from .helpers import (
    validate_equally_dist_expense,
    validate_unequally_dist_expense,
    simplify_debts,
    construct_netbalance,
)
from .constants import INVALID_TRANSACTION


class ExpenseService:
    """
    This class contains all the service methods for Expense model
    """
    def add_an_expense(validated_data, user):
        """
        Service to add an expense to a group
        """
        group_name = validated_data['group_name']
        splitting_category = validated_data['splitting_category']

        # We need to check if the group exists
        GroupService.validate_group(name=group_name)

        # Bifurcating to 2 different child services based on flow
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

        # Creating an expense and corresponding ledger entries
        ExpenseService.create_expense(
            validated_data=validated_data,
            username_share_mapping=username_share_mapping,
            user=user,

        )

    def add_equally_dist_expense(validated_data, user):
        """
        Child Service to add an equally distributed expense
        """
        username_share_mapping = validate_equally_dist_expense(
            validated_data=validated_data,
        )

        return username_share_mapping

    def add_unequally_dist_expense(validated_data, user):
        """
        Child Service to add an unequally distributed expense
        """
        username_share_mapping = validate_unequally_dist_expense(
            validated_data=validated_data,
        )

        return username_share_mapping

    def create_expense(validated_data, username_share_mapping, user):
        """
        Majot Service to create an expense
        """
        paid_by = validated_data['paid_by']
        group_name = validated_data['group_name']

        # Since data has been already verified, we can directly retrieve them
        paid_by = UserService.retrieve_user_objects(usernames=[paid_by]).last()
        shared_with_users = UserService.retrieve_user_objects(
            usernames=list(username_share_mapping.keys()),
        )
        group = GroupService.retrieve_group_object(name=group_name)

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

        # Service responsible for adding entries in the ledger
        ExpenseService.add_expense_in_ledger(
            expense=expense, username_share_mapping=username_share_mapping,
        )

        return expense

    def add_expense_in_ledger(expense, username_share_mapping):
        """
        Child service for adding details in the ledger

        username_share_mapping is a dictionary that represents how
        much money is owed by people involved in a expense
        """
        for username, split in username_share_mapping.items():
            debit_from = UserService.retrieve_user_objects(usernames=[username]).last()
            amount = Decimal(split)

            # We are not adding an entry for self-share in the ledger
            if debit_from == expense.paid_by:
                continue

            lt_object = LedgerTimeline.objects.create(
                event=LedgerTimeline.EXPENSE,
                credit_to=expense.paid_by,
                debit_from=debit_from,
                amount=amount,
                expense=expense,
                group=expense.group,
                created_by=expense.created_by,
            )

            ledger_entry = ExpenseService.fetch_or_create_ledgre_entry(lt_object=lt_object)
            ledger_entry.amount = ledger_entry.amount + amount
            ledger_entry.save(update_fields=['amount', 'updated_at'])

    def add_settlement_in_ledger(validated_data, user):
        """
        Service for adding a settlement in the ledger
        """
        settled_by_username = validated_data['settled_by']
        paying_to_username = validated_data['paying_to']
        amount = validated_data['amount']
        group_name = validated_data['group_name']

        # User cannot settle against himself
        if settled_by_username == paying_to_username:
            raise ParseError(INVALID_TRANSACTION)

        group = GroupService.retrieve_group_object(name=group_name)
        settled_by = UserService.retrieve_user_objects([settled_by_username]).last()
        paying_to = UserService.retrieve_user_objects([paying_to_username]).last()

        lt_object = LedgerTimeline.objects.create(
            event=LedgerTimeline.SETTLEMENT,
            credit_to=paying_to,
            debit_from=settled_by,
            amount=amount,
            expense=None,
            group=group,
            created_by=user,
        )

        ledger_entry = ExpenseService.fetch_or_create_ledgre_entry(lt_object=lt_object)
        ledger_entry.amount = ledger_entry.amount - amount
        ledger_entry.save(update_fields=['amount', 'updated_at'])

    def fetch_or_create_ledgre_entry(lt_object):
        """
        Service to maintin entries in the ledger

        There will be 2 entries per user AT MAX against a group:
            1. He will be the creditor
            2. He will be the debtor
        """

        ledger_entry = Ledger.objects.filter(
            credit_to=lt_object.credit_to,
            debit_from=lt_object.debit_from,
            group=lt_object.group,
            is_active=True,
        ).last()

        if ledger_entry is None:
            ledger_entry = Ledger.objects.create(
                credit_to=lt_object.credit_to,
                debit_from=lt_object.debit_from,
                group=lt_object.group,
            )

        return ledger_entry

    def fetch_balance(validated_data, user):
        """
        Service to fetch balance for a user in total or for a specific group
        """
        group_name = validated_data['group_name']

        # Fetching Balance only in a specific group
        if group_name is not None:
            # Grouping based on people he owes money
            you_owe = Ledger.objects.filter(
                debit_from=user, group__name=group_name, is_active=True,
            ).values('credit_to__username').annotate(Sum('amount'))

            response = []
            for record in you_owe:
                mapping = {
                    'username': record['credit_to__username'],
                    'you_owe': record['amount__sum'],
                }
                response.append(mapping)
        else:
            # Grouping based on people he owes money
            you_owe = Ledger.objects.filter(
                debit_from=user, is_active=True,
            ).values('credit_to__username').annotate(Sum('amount'))

            response = []
            for record in you_owe:
                mapping = {
                    'username': record['credit_to__username'],
                    'you_owe': record['amount__sum'],
                }
                response.append(mapping)

        return response

    def check_for_zero_balance(members):
        """
        Service to verify zero balance for a user
        before removing a him from the requested group
        """
        you_owe = Ledger.objects.filter(debit_from__in=members, is_active=True, amount__gt=0)
        you_are_owed = Ledger.objects.filter(credit_to__in=members, is_active=True, amount__gt=0)
        if you_owe.count() != 0 or you_are_owed.count() != 0:
            return False
        return True

    def simplify_debts(validated_data):
        """
        Service that tries to reduce the number of transactions in a group
        """
        group_name = validated_data['group_name']
        group = GroupService.retrieve_group_object(name=group_name)

        all_transactions = Ledger.objects.filter(group=group, is_active=True)

        net_balance = construct_netbalance(all_transactions)
        username_share_mapping = simplify_debts(net_balance=net_balance)

        # Marking old transactions as inactive and creating new ones
        all_transactions.update(is_active=False)

        for txn in username_share_mapping:
            credit_to = UserService.retrieve_user_objects(usernames=[txn['credit_to']]).last()
            debit_from = UserService.retrieve_user_objects(usernames=[txn['debit_from']]).last()
            Ledger.objects.create(
                credit_to=credit_to,
                debit_from=debit_from,
                amount=txn['amount'],
                group=group,
            )

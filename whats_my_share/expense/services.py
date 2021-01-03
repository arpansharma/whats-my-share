# django / rest-framework imports
from rest_framework.exceptions import ParseError

# project level imports
from accounts.services import UserService, GroupService

# app level imports
from .models import Expense, LedgerTimeline, Ledger
from .helpers import (
    validate_equally_dist_expense,
    validate_unequally_dist_expense,
)
from .constants import INVALID_TRANSACTION


class ExpenseService:
    def add_an_expense(validated_data, user):
        group_name = validated_data['group_name']
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
        paid_by = validated_data['paid_by']
        group_name = validated_data['group_name']

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

        ExpenseService.add_expense_in_ledger(
            expense=expense, username_share_mapping=username_share_mapping,
        )

        return expense

    def add_expense_in_ledger(expense, username_share_mapping):
        for username, split in username_share_mapping.items():
            debit_from = UserService.retrieve_user_objects(usernames=[username]).last()
            amount = split

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
        settled_by_username = validated_data['settled_by']
        paying_to_username = validated_data['paying_to']
        amount = validated_data['amount']
        group_name = validated_data['group_name']

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
        ledger_entry = Ledger.objects.filter(
            credit_to=lt_object.credit_to,
            debit_from=lt_object.debit_from,
            group=lt_object.group,
        ).last()

        if ledger_entry is None:
            ledger_entry = Ledger.objects.create(
                credit_to=lt_object.credit_to,
                debit_from=lt_object.debit_from,
                group=lt_object.group,
            )

        return ledger_entry

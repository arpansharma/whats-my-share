# django/rest-framework imports
from django.contrib import admin

# app level imports
from .models import Expense, LedgerTimeline, Ledger, LedgerSimplified


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'amount',
        'paid_by',
        'created_by',
        'splitting_category',
        'get_shared_with_users',
        'group',
        'created_at',
        'updated_at',
        'notes',
        'comments',

    )

    def get_shared_with_users(self, obj):
        return ", ".join([user.username for user in obj.shared_with_users.all()])


@admin.register(LedgerTimeline)
class LedgerTimelineAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'credit_to',
        'debit_from',
        'event',
        'amount',
        'expense',
        'group',
        'created_by',
        'created_at',
        'updated_at',
    )


@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'credit_to',
        'debit_from',
        'amount',
        'group',
        'is_active',
        'created_at',
        'updated_at',
    )


@admin.register(LedgerSimplified)
class LedgerSimplifiedAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'credit_to',
        'debit_from',
        'amount',
        'group',
        'is_active',
        'created_at',
        'updated_at',
    )

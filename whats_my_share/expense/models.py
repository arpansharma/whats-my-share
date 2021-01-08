# django/rest-framework imports
from django.db import models


class Expense(models.Model):
    EQUALLY = 'equally'
    BY_PERCENTAGE = 'by_percentage'
    BY_AMOUNT = 'by_amount'

    SPLITTING_CATEGORY_CHOICES = (
        (EQUALLY, 'Equally'),
        (BY_PERCENTAGE, 'By Percentage'),
        (BY_AMOUNT, 'By Amount'),
    )

    title = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    paid_by = models.ForeignKey('accounts.user', related_name="paid_for_expense", on_delete=models.PROTECT)
    splitting_category = models.CharField(max_length=16, choices=SPLITTING_CATEGORY_CHOICES)
    shared_with_users = models.ManyToManyField('accounts.User', related_name='part_of_expense')
    group = models.ForeignKey('accounts.Group', related_name="expense", on_delete=models.PROTECT)
    notes = models.TextField(null=True, default=None)
    comments = models.TextField(null=True, default=None)
    created_by = models.ForeignKey('accounts.User', related_name="created_expense", on_delete=models.PROTECT)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        app_label = 'expense'
        db_table = 'api_expense'
        verbose_name_plural = 'Expenses'


class LedgerTimeline(models.Model):
    EXPENSE = 'expense'
    SETTLEMENT = 'settlement'
    EVENT_CHOICES = (
        (EXPENSE, 'Shared an Expense'),
        (SETTLEMENT, 'Did a Settlement'),
    )

    event = models.CharField(max_length=16, choices=EVENT_CHOICES)
    credit_to = models.ForeignKey('accounts.user', related_name="credit_to_lt", on_delete=models.PROTECT)
    debit_from = models.ForeignKey('accounts.user', related_name="debit_from_lt", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    expense = models.ForeignKey('expense.Expense', related_name="expense_lt", on_delete=models.PROTECT, null=True)
    group = models.ForeignKey('accounts.Group', related_name="group_lt", on_delete=models.PROTECT)
    created_by = models.ForeignKey('accounts.User', related_name="created_by_lt", on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        app_label = 'expense'
        db_table = 'api_ledger_timeline'
        verbose_name_plural = 'Ledger Timeline'


class Ledger(models.Model):
    credit_to = models.ForeignKey('accounts.user', related_name="credit_to_ld", on_delete=models.PROTECT)
    debit_from = models.ForeignKey('accounts.user', related_name="debit_from_ld", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    group = models.ForeignKey('accounts.Group', related_name="group_ld", on_delete=models.PROTECT)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        app_label = 'expense'
        db_table = 'api_ledger'
        verbose_name_plural = 'Ledger'

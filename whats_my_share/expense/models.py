# django/rest-framework imports
from django.db import models


class Expense(models.Model):

    SPLITTING_CATEGORY_CHOICES = (
        ('equally', 'Equally'),
        ('by_percentage', 'By Percentage'),
        ('by_amount', 'By Amount'),
    )

    title = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    paid_by = models.ForeignKey('accounts.user', related_name="paid_for_expense", on_delete=models.PROTECT)
    splitting_category = models.CharField(max_length=16, choices=SPLITTING_CATEGORY_CHOICES)
    shared_with_users = models.ManyToManyField('accounts.User', related_name='part_of_expense')
    group = models.ForeignKey('accounts.Group', related_name="expense", on_delete=models.PROTECT)
    notes = models.TextField()
    comments = models.TextField()

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
    EVENT_CHOICES = (
        ('expense', 'Shared an Expense'),
        ('settlement', 'Did a Settlement'),
    )

    event = models.CharField(max_length=16, choices=EVENT_CHOICES)
    credit_to = models.ForeignKey('accounts.user', related_name="credit_to_lt", on_delete=models.PROTECT)
    debit_from = models.ForeignKey('accounts.user', related_name="debit_from_lt", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    expense = models.ForeignKey('expense.Expense', related_name="expense_lt", on_delete=models.PROTECT)
    created_by = models.ForeignKey('accounts.User', related_name="created_by_lt", on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

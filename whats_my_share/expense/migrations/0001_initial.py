# Generated by Django 2.2 on 2021-01-02 11:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_group'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('splitting_category', models.CharField(choices=[('equally', 'Equally'), ('by_percentage', 'By Percentage'), ('by_amount', 'By Amount')], max_length=16)),
                ('notes', models.TextField()),
                ('comments', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='expense', to='accounts.Group')),
                ('paid_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='paid_for_expense', to=settings.AUTH_USER_MODEL)),
                ('shared_with_users', models.ManyToManyField(related_name='part_of_expense', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Expenses',
                'db_table': 'api_expense',
            },
        ),
    ]

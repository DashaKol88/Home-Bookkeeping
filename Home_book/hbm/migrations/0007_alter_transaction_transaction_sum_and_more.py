# Generated by Django 4.1.7 on 2023-03-01 14:45

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("hbm", "0006_alter_transaction_transaction_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="transaction_sum",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.CreateModel(
            name="PlanningTransaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transaction_type_plan",
                    models.IntegerField(
                        choices=[(0, "Expense"), (1, "Income")], default=0
                    ),
                ),
                (
                    "transaction_date_plan",
                    models.DateField(default=django.utils.timezone.now),
                ),
                (
                    "transaction_sum_plan",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                    ),
                ),
                ("transaction_comment_plan", models.CharField(max_length=255)),
                (
                    "transaction_account_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="hbm.account"
                    ),
                ),
                (
                    "transaction_category_plan",
                    models.ForeignKey(
                        default=0,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to="hbm.transactioncategory",
                    ),
                ),
            ],
        ),
    ]

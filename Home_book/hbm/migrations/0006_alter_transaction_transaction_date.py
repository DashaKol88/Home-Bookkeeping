# Generated by Django 4.1.7 on 2023-02-26 19:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("hbm", "0005_remove_transaction_transaction_balance_now"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="transaction_date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]

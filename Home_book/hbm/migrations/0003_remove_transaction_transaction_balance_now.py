# Generated by Django 4.1.7 on 2023-02-20 17:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("hbm", "0002_alter_account_account_balance"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction", name="transaction_balance_now",
        ),
    ]

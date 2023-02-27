from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.
class Account(models.Model):
    account_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=200, null=False, blank=False)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.account_owner} {self.account_number} {self.account_balance}'

class TransactionCategory(models.Model):
    category_type_choices = [(0, 'Expense'), (1, 'Income')]
    category_type = models.IntegerField(choices=category_type_choices, default=0)
    category_name = models.CharField(max_length=255, default='None')

    def __str__(self):
        return self.category_name

class Transaction(models.Model):
    transaction_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type_choices = [(0, 'Expense'), (1, 'Income')]
    transaction_type = models.IntegerField(choices=transaction_type_choices, default=0)
    transaction_category = models.ForeignKey(TransactionCategory, on_delete=models.SET_DEFAULT, default=0)
    transaction_date = models.DateField(default=timezone.now)
    transaction_sum = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_comment = models.CharField(max_length=255)



    def __str__(self):
        return f"{self.transaction_type_choices[self.transaction_type][1]}; Sum:{self.transaction_sum}; Date:{self.transaction_date}"



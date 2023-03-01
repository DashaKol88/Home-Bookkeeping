from django.contrib import admin
from .models import Account, Transaction, TransactionCategory, PlanningTransaction

# Register your models here.
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(TransactionCategory)
admin.site.register(PlanningTransaction)
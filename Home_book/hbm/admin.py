from django.contrib import admin
from .models import Account, Transaction, TransactionCategory, PlanningTransaction


# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = (
        "transaction_account", "transaction_type", "transaction_category", "transaction_sum", "transaction_comment",
        "transaction_date")
    list_filter = ("transaction_date",)


class PlanningTransactionAdmin(admin.ModelAdmin):
    model = PlanningTransaction
    list_display = (
        "transaction_account_plan", "transaction_type_plan", "transaction_category_plan", "transaction_sum_plan",
        "transaction_comment_plan",
        "transaction_date_plan")
    list_filter = ("transaction_date_plan",)


class TransactionInstanceInline(admin.TabularInline):
    model = Transaction


class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ("category_type", "category_name")


class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_owner", "account_number", "account_balance")
    inlines = [TransactionInstanceInline]


admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionCategory, TransactionCategoryAdmin)
admin.site.register(PlanningTransaction, PlanningTransactionAdmin)

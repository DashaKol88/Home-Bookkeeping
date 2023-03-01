from django import forms
from .models import Transaction, PlanningTransaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            'transaction_type', 'transaction_category', 'transaction_date', 'transaction_sum', 'transaction_comment')


class PlanningTransactionForm(forms.ModelForm):
    class Meta:
        model = PlanningTransaction
        fields = (
            'transaction_type_plan', 'transaction_category_plan', 'transaction_date_plan', 'transaction_sum_plan',
            'transaction_comment_plan')

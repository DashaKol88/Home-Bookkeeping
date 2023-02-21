from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            'transaction_type', 'transaction_category', 'transaction_date', 'transaction_sum', 'transaction_comment')

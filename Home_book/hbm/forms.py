from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Transaction, PlanningTransaction
from django.forms import DateInput


def validate_not_future_date(value: date) -> None:
    """
    Function to return an error if the transaction date is in the future
    """
    if value > date.today():
        raise ValidationError({'transaction_date': [f'{value} is in the future']})


def validate_not_past_date(value: date) -> None:
    """
    Function for throwing an error if the date of the planned transaction is in the past
    """
    if value < date.today():
        raise ValidationError({'transaction_date_plan': [f'{value} is in the past']})


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            'transaction_type', 'transaction_category', 'transaction_date', 'transaction_sum', 'transaction_comment')
        widgets = {'transaction_date': DateInput(attrs={'type': 'date'}), }

    def clean(self):
        """
        clean() override for custom validators call
        """
        super().clean()
        validate_not_future_date(self.cleaned_data.get('transaction_date'))


class PlanningTransactionForm(forms.ModelForm):
    class Meta:
        model = PlanningTransaction
        fields = (
            'transaction_type_plan', 'transaction_category_plan', 'transaction_date_plan', 'transaction_sum_plan',
            'transaction_comment_plan')
        widgets = {'transaction_date_plan': DateInput(attrs={'type': 'date'}), }

    def clean(self):
        """
        clean() override for custom validators call
        """
        super().clean()
        validate_not_past_date(self.cleaned_data.get('transaction_date_plan'))

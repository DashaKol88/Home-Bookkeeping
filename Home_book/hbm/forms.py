from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Transaction, PlanningTransaction
from django.forms import DateInput


def validate_not_future_date(value):
    if value > date.today():
        raise ValidationError('%s is in the future' % value)


def validate_not_past_date(value):
    if value < date.today():
        raise ValidationError('%s is in the past' % value)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            'transaction_type', 'transaction_category', 'transaction_date', 'transaction_sum', 'transaction_comment')
        widgets = {'transaction_date': DateInput(attrs={'type': 'date'}), }

    def clean(self):
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
        super().clean()
        validate_not_past_date(self.cleaned_data.get('transaction_date_plan'))

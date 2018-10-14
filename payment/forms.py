import datetime

from django import forms
from django.forms import Select, Textarea, NumberInput
from django.utils.translation import ugettext_lazy as _

from payment.models import Payment, PaymentRegister


class PaymentRegisterForm(forms.ModelForm):

    class Meta:
        model = PaymentRegister
        exclude = ['service', 'total', 'installment_value']

        widgets = {
            'installment': Select(attrs={'class': 'form-control', 'onchange': 'updateInput()'}),
            'discount_or_increase': NumberInput(attrs={'class': 'form-control', 'onchange': 'updateInput()'}),
            'note': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
        }


class PaymentForm(forms.ModelForm):
    date = forms.DateField(
        input_formats=['%d/%m/%Y'], required=True, initial=datetime.date.today, widget=forms.DateInput(
            attrs={'class': 'form-control datepicker', 'data-error': _('This field must be filled.')},
            format='%d/%m/%Y')
    )

    class Meta:
        model = Payment
        exclude = ['payment_register']

        widgets = {
            'payment_method': Select(attrs={'class': 'form-control'})
        }

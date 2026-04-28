import re
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import ServicePrice, ServiceTransaction


def validate_name(value):
    value = value.strip()
    if len(value) < 3:
        raise forms.ValidationError("Name must be at least 3 characters.")
    if not value[0].isupper():
        raise forms.ValidationError("Name must start with a capital letter.")
    if not re.match(r'^[A-Za-z\s\-]+$', value):
        raise forms.ValidationError("Name must contain letters only.")
    return value


def validate_phone(value):
    phone = value.strip().replace(' ', '').replace('+256', '0')
    if not re.match(r'^(07|06)\d{8}$', phone):
        raise forms.ValidationError("Please Enter a valid phone number in this format(e.g. 0700123456).")
    return phone


class ServicePriceForm(forms.ModelForm):
    class Meta:
        model  = ServicePrice
        fields = ['service_type', 'price']
        widgets = {
            'price': forms.NumberInput(attrs={'min': 0, 'step': '500', 'placeholder': 'e.g. 5000'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'service_type',
            'price',
            Submit('submit', 'Save Price', css_class='btn btn-primary mt-2'),
        )

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None or price < 0:
            raise forms.ValidationError("Price must be zero or more.")
        return price


class TyreTransactionForm(forms.ModelForm):
    class Meta:
        model  = ServiceTransaction
        fields = ['service', 'customer_name', 'phone', 'amount', 'date']
        widgets = {
            'date':   forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'min': 0, 'step': '500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only tyre services
        self.fields['service'].queryset = ServicePrice.objects.filter(
            service_type__startswith='tyre'
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('customer_name', css_class='col-md-6'),
                Column('phone',         css_class='col-md-6'),
            ),
            Row(
                Column('service', css_class='col-md-6'),
                Column('amount',  css_class='col-md-6'),
            ),
            'date',
            Submit('submit', '🔧 Record Tyre Service', css_class='btn btn-warning mt-2 w-100 fw-bold'),
        )

    def clean_customer_name(self):
        return validate_name(self.cleaned_data.get('customer_name', ''))

    def clean_phone(self):
        return validate_phone(self.cleaned_data.get('phone', ''))

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class BatteryTransactionForm(forms.ModelForm):
    class Meta:
        model  = ServiceTransaction
        fields = ['service', 'customer_name', 'phone', 'amount', 'date']
        widgets = {
            'date':   forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'min': 0, 'step': '500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only battery services
        self.fields['service'].queryset = ServicePrice.objects.filter(
            service_type__startswith='battery'
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('customer_name', css_class='col-md-6'),
                Column('phone',         css_class='col-md-6'),
            ),
            Row(
                Column('service', css_class='col-md-6'),
                Column('amount',  css_class='col-md-6'),
            ),
            'date',
            Submit('submit', '🔋 Record Battery Service', css_class='btn btn-primary mt-2 w-100 fw-bold'),
        )

    def clean_customer_name(self):
        return validate_name(self.cleaned_data.get('customer_name', ''))

    def clean_phone(self):
        return validate_phone(self.cleaned_data.get('phone', ''))

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

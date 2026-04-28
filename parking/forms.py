import re
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Vehicle, SignOut


# ─────────────────────────────────────────────────────────
#  Shared validation helpers
# ─────────────────────────────────────────────────────────

def validate_name(value, label="Name"):
    value = value.strip()
    if len(value) < 3:
        raise forms.ValidationError(f"{label} must be at least 3 characters.")
    if not value[0].isupper():
        raise forms.ValidationError(f"{label} must start with a capital letter.")
    if not re.match(r'^[A-Za-z\s\-]+$', value):
        raise forms.ValidationError(f"{label} must contain letters only — no numbers or symbols.")
    return value


def validate_phone(value):
    phone = value.strip().replace(' ', '').replace('+256', '0')
    if not re.match(r'^(07|06)\d{8}$', phone):
        raise forms.ValidationError(
            "Enter a valid Ugandan phone number. Example: 0701234567 or 0772345678"
        )
    return phone


def validate_nin(value):
    """
    Uganda NIN — exactly 14 alphanumeric characters.
    Starts with 2 letters (district code), followed by 12 alphanumeric characters.
    Example: CM900000001234
    """
    nin = value.strip().upper()
    if not re.match(r'^[A-Z]{2}[A-Z0-9]{12}$', nin):
        raise forms.ValidationError(
            "NIN must be exactly 14 characters — 2 letters then 12 alphanumeric. "
            "Example: CM900000001234"
        )
    return nin


# ─────────────────────────────────────────────────────────
#  Vehicle Registration Form
# ─────────────────────────────────────────────────────────

class VehicleRegistrationForm(forms.ModelForm):

    class Meta:
        model  = Vehicle
        fields = ['driver_name', 'vehicle_type', 'plate_number',
                  'model_color', 'phone', 'nin']
        widgets = {
            'plate_number': forms.TextInput(attrs={
                'placeholder': 'e.g. UBA123X',
                'style': 'text-transform:uppercase;letter-spacing:2px;'
                         'font-family:monospace;font-weight:600',
            }),
            'nin': forms.TextInput(attrs={
                'placeholder': 'e.g. CM900000001234',
                'style': 'text-transform:uppercase;font-family:monospace;letter-spacing:1px',
                'maxlength': '14',
            }),
            'driver_name':  forms.TextInput(attrs={'placeholder': 'e.g. John Baptist Ssemuwemba'}),
            'model_color':  forms.TextInput(attrs={'placeholder': 'e.g. Toyota Harrier, Silver'}),
            'phone':        forms.TextInput(attrs={'placeholder': '0700 000 000'}),
        }
        help_texts = {
            'plate_number': 'Must start with U, alphanumeric only, max 8 characters.',
            'nin':          'Required for Boda-boda only. Exactly 14 characters — e.g. CM900000001234',
            'phone':        'Ugandan number: 0700000000 or 0772000000',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nin'].required = False
        self.helper = FormHelper()
        self.helper.form_tag = False  # we write <form> manually in templates

    def clean_driver_name(self):
        return validate_name(self.cleaned_data.get('driver_name', ''), 'Driver name')

    def clean_plate_number(self):
        plate = self.cleaned_data.get('plate_number', '').strip().upper().replace(' ', '')
        if not plate:
            raise forms.ValidationError("Plate number cannot be blank.")
        if not plate.startswith('U'):
            raise forms.ValidationError("Plate number must start with the letter U.")
        if not re.match(r'^U[A-Z0-9]{2,7}$', plate):
            raise forms.ValidationError(
                "Plate must be alphanumeric, start with U, and be under 8 characters. "
                "Example: UBA123X"
            )
        return plate

    def clean_phone(self):
        return validate_phone(self.cleaned_data.get('phone', ''))

    def clean_nin(self):
        nin          = self.cleaned_data.get('nin', '').strip().upper()
        vehicle_type = self.cleaned_data.get('vehicle_type')
        if vehicle_type == 'boda_boda' and not nin:
            raise forms.ValidationError("NIN is required for all Boda-boda registrations.")
        if nin:
            return validate_nin(nin)
        return nin

    def clean_model_color(self):
        value = self.cleaned_data.get('model_color', '').strip()
        if not value:
            raise forms.ValidationError("Vehicle model and colour cannot be blank.")
        return value


# ─────────────────────────────────────────────────────────
#  Vehicle Edit Form
# ─────────────────────────────────────────────────────────

class VehicleEditForm(VehicleRegistrationForm):
    """Identical validation — used on the edit page."""
    pass


# ─────────────────────────────────────────────────────────
#  Sign-Out Search
# ─────────────────────────────────────────────────────────

class VehicleSearchForm(forms.Form):
    search = forms.CharField(
        label='Plate Number',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. UBA123X',
            'style': 'text-transform:uppercase;letter-spacing:1.5px;'
                     'font-family:monospace;font-weight:600',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_tag = False


# ─────────────────────────────────────────────────────────
#  Sign-Out Receiver Form
# ─────────────────────────────────────────────────────────

class SignOutForm(forms.ModelForm):

    class Meta:
        model  = SignOut
        fields = ['receiver_name', 'receiver_phone', 'receiver_gender', 'receiver_nin']
        widgets = {
            'receiver_nin': forms.TextInput(attrs={
                'placeholder': 'e.g. CM900000001234',
                'style': 'text-transform:uppercase;font-family:monospace;letter-spacing:1px',
                'maxlength': '14',
            }),
            'receiver_name':  forms.TextInput(attrs={'placeholder': 'As shown on National ID'}),
            'receiver_phone': forms.TextInput(attrs={'placeholder': '0700 000 000'}),
        }
        help_texts = {
            'receiver_nin':  'Exactly 14 characters. Example: CM900000001234',
            'receiver_phone': 'Ugandan number: 0700000000',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_receiver_name(self):
        return validate_name(self.cleaned_data.get('receiver_name', ''), 'Receiver name')

    def clean_receiver_phone(self):
        return validate_phone(self.cleaned_data.get('receiver_phone', ''))

    def clean_receiver_nin(self):
        nin = self.cleaned_data.get('receiver_nin', '').strip().upper()
        if not nin:
            raise forms.ValidationError("NIN is required for vehicle sign-out.")
        return validate_nin(nin)

    def clean_receiver_gender(self):
        value = self.cleaned_data.get('receiver_gender', '')
        if not value:
            raise forms.ValidationError("Please select a gender.")
        return value

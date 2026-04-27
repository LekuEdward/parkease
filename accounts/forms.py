from django import forms
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from .models import CustomUser


class LoginForm(AuthenticationForm):
    """Login form styled with crispy forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter your username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Enter your password'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username'),
            Field('password'),
            Submit('submit', 'Sign In to Dashboard',
                   css_class='btn btn-success w-100 mt-2 py-2 fw-bold'),
        )


class UserCreateForm(forms.ModelForm):
    """Admin form to create new users."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Set a password'}),
        label='Password'
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'password',
            Submit('submit', 'Create User', css_class='btn btn-primary mt-2'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control'
        })
    )

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First name',
            'class': 'form-control'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']

        widgets = {
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Enter phone number',
                'class': 'form-control'
            }),

            'address': forms.Textarea(attrs={
                'placeholder': 'Enter delivery address',
                'class': 'form-control',
                'rows': 3
            })
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()

        if phone and not phone.replace('+', '').replace(' ', '').isdigit():
            raise forms.ValidationError(
                "Please enter a valid phone number."
            )

        return phone

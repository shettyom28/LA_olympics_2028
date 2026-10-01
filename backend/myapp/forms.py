from django import forms
from django.contrib.auth.models import User
from .models import Country

class ExampleMessageForm(forms.Form):
    content = forms.CharField()

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[('staff', 'Staff'), ('athlete', 'Athlete'), ('spectator', 'Spectator')], initial='spectator')
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already registered.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class EditUserProfileForm(forms.Form):
    role = forms.ChoiceField(choices=[('staff', 'Staff'), ('athlete', 'Athlete'), ('spectator', 'Spectator')])
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False)

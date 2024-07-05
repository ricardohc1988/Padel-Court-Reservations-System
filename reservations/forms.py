from django import forms
from .models import Reservation, Court
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from datetime import date

class ReservationForm(forms.ModelForm):
    START_TIME_CHOICES = [(f"{hour:02}:00", f"{hour:02}:00") for hour in range(7, 23)]
    END_TIME_CHOICES = [(f"{hour:02}:00", f"{hour:02}:00") for hour in range(8, 24)]

    start_time = forms.ChoiceField(choices=START_TIME_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    end_time = forms.ChoiceField(choices=END_TIME_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': date.today().strftime}))
    court = forms.ModelChoiceField(queryset=Court.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Reservation
        fields = ['court', 'date', 'start_time', 'end_time']

class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, help_text='Required.', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, help_text='Required.', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class UserAccountUpdateForm(UserChangeForm):   
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.PasswordInput()

class CodeVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Code'}))
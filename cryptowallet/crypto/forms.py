from django.contrib.auth.models import User
from django import forms
from .models import Transaction,Account


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Account
        fields = ['username','email','password']


class TransactionForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Transaction
        fields = ['from_address','to_address','amount','password']
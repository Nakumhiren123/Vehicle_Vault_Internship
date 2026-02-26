from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class UserSignupForm(UserCreationForm):
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    class Meta:
        model = User
        fields = ('first_name','last_name','email','gender','role', 'password1', 'password2')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
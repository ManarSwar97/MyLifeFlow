from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class NewSignupForm(UserCreationForm):

    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    profile_image = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
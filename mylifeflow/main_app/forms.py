from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Person, Task
import datetime

class NewSignupForm(UserCreationForm):

    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    profile_image = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class PersonForm(forms.ModelForm):
    contact_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Next Contact Date"
    )

    class Meta:
        model = Person
        fields = ['name', 'relationship', 'contact_date', 'notes']

    def clean_contact_date(self):
        contact_date = self.cleaned_data['contact_date']
        if contact_date <= datetime.date.today():
            raise forms.ValidationError("Next Contact Date must be after today.")
        return contact_date
    
class TaskForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    is_completed = forms.BooleanField(required=False, label="Completed?")


    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'is_completed']
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Person, Task, Budget, Expense,  Grocery
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
        fields = ['name', 'relationship', 'email', 'contact_date', 'notes']

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

class BudgetForm(forms.ModelForm):
    class Meta:
        model= Budget
        fields=[ 'name', 'type', 'total_amount','duration_type','start_date', 'end_date','auto_daily_limit', 'manual_daily_limit','saving_goal']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'auto_daily_limit': forms.CheckboxInput(attrs={'class': 'filled-in'})
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model= Expense
        fields=['name', 'amount', 'frequency', 'budget']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  #check the user
        super().__init__(*args, **kwargs)
        if user:
            self.fields['budget'].queryset = Budget.objects.filter(user=user) #dropdown box for the budget list
        else:
            # no budget if the user not exist
            self.fields['budget'].queryset = Budget.objects.none()

    
class GroceryForm(forms.ModelForm):
    purchase_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Purchase Date"
    )

    class Meta:
        model = Grocery
        fields = ['name', 'purchase_date', 'duration_days', 'notes', 'is_restocked']

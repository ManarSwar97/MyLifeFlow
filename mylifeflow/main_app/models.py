from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
#extending the user model by creating another model and make one-to-one relationship between them 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField()
    profile_image = models.ImageField(upload_to='main_app/static/uploads/', default="")

    def __str__(self):
        return self.user.username

class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.id})
    

class Budget(models.Model):
    #to be as drop box
    #(value, label)
    TYPE_OPTIONS = [
        ('salary', 'Salary'),
        ('saving', 'Saving'),
        ('custom', 'Custom'),
    ]

    DURATION_OPTIONS = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('custom', 'Start-End Date'),
    ]

    name= models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=TYPE_OPTIONS ) #choices to make it drop box
    total_amount= models.DecimalField(max_digits=10, decimal_places=2)
    duration_type= models.CharField(max_length=10, choices=DURATION_OPTIONS)
    start_date= models.DateField()
    end_date= models.DateField()
    auto_daily_limit= models.BooleanField(default=True)
    manual_daily_limit= models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) #null for the database , blank for the form
    saving_goal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Budget: {self.name} {self.user.username}"
    
    def get_days_count(self):
        return (self.end_date - self.start_date).days + 1
    #.days it give the number if days between two dates +1 because for ex 1 - 5 = 4 days the start day is missing so + 1

    def daily_limit(self):
        if self.auto_daily_limit:
            days = self.get_days_count() or 1  # prevent division by zero
            remaining = self.total_amount - self.total_planned_expenses()
            return round(remaining / days,2)
        return self.manual_daily_limit

    
    def total_planned_expenses(self):
        return sum(expense.amount for expense in self.expense_set.all()) #calculate all expenses

    def get_absolute_url(self):
        return reverse('budget_detail', kwargs={'pk': self.pk})


class Expense(models.Model):
    FREQUENCY_OPTIONS = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('one-time', 'One-Time'),
    ]
    budget=models.ForeignKey(Budget, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    frequency=models.CharField(max_length=10, choices=FREQUENCY_OPTIONS)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('expense_detail', kwargs={'pk': self.pk})



    
class Note(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField()
    image = models.ImageField(upload_to='main_app/static/uploads', default="")
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Note: {self.title}"
    

class Grocery(models.Model):
    name = models.CharField(max_length=50)
    purchase_date = models.DateField()
    duration_days = models.IntegerField()
    next_restock= models.DateField()
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Grocery: {self.name}"


class Item(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    description = models.TextField()
    qr_code_url = models.URLField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    movement = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    def __str__(self):
        return f"Item: {self.name}"


class Person(models.Model):
    name = models.CharField(max_length=50)
    relationship = models.CharField(max_length=50)
    contact_date = models.DateField()
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"
    
    def get_absolute_url(self):
        return reverse('person_detail', kwargs={'pk': self.id})


class Achievement(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"



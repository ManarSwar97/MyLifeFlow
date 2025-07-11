from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
import datetime


# Create your models here.
#extending the user model by creating another model and make one-to-one relationship between them 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField()
    profile_image = models.ImageField(upload_to='main_app/static/uploads/', default="")
    latitude= models.FloatField(default=0.0)
    longitude= models.FloatField(default=0.0)
    
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
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('expense_detail', kwargs={'pk': self.pk})


class Note(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField(max_length=1500)
    image = models.ImageField(upload_to='main_app/static/uploads', default="")
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Note: {self.title}"
    def get_absolute_url(self):
        return reverse('note_detail', kwargs={'pk': self.id})    


class Voice(models.Model):
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('calm', 'Calm'),
        ('excited', 'Excited'),
        ('anxious', 'Anxious'),
        ('tired', 'Tired'),
        ('neutral', 'Neutral'),
    ]
    title = models.CharField(max_length=50)
    audio = models.FileField(upload_to='audio/', blank=True, null=True)
    image = models.ImageField(upload_to='main_app/static/uploads', default="")
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES, default='neutral')

    def __str__(self):
        return f"Voicenote: {self.title}"
    def get_absolute_url(self):
        return reverse('voice_detail', kwargs={'pk': self.id})   
    

class Grocery(models.Model):
    name = models.CharField(max_length=50)
    purchase_date = models.DateField()
    duration_days = models.IntegerField()
    notes = models.TextField(blank=True)
    is_restocked = models.BooleanField(default=False)
    restock_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Grocery: {self.name}"
    
    def get_absolute_url(self):
        return reverse('grocery_detail', kwargs={'pk': self.id})
    
    def save(self, *args, **kwargs):
        if self.is_restocked and not self.restock_date:
            self.restock_date = timezone.now().date()
        elif not self.is_restocked:
            self.restock_date = None
        super().save(*args, **kwargs)

    @property
    def next_restock(self):
        return self.purchase_date + timedelta(days=self.duration_days)


class Item(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    movement = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )

    def __str__(self):
        return f"Item: {self.name}"

    def get_absolute_url(self):
        return reverse('item_detail', kwargs={'pk': self.id})



class Person(models.Model):
    name = models.CharField(max_length=50)
    relationship = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    contact_date = models.DateField()
    notes = models.TextField(blank=True)
    interact_times = models.IntegerField(default=0)
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


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"
    

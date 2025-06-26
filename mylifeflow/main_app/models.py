from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from datetime import date
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
    

class Budget(models.Model):
    income = models.DecimalField(max_digits=7, decimal_places=2)
    daily_limit = models.DecimalField(max_digits=7, decimal_places=2)
    saving_goal = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Budget: {self.income}"
    
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



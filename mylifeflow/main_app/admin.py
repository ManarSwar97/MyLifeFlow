from django.contrib import admin
from .models import Task, Budget, Note, Grocery, Item, Person, Achievement, UserProfile, Expense, Voice, Message
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Task)
admin.site.register(Budget)
admin.site.register(Expense)
admin.site.register(Note)
admin.site.register(Grocery)
admin.site.register(Item)
admin.site.register(Person)
admin.site.register(Achievement)
admin.site.register(Voice)
admin.site.register(Message)
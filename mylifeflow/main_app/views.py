from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import NewSignupForm, PersonForm, TaskForm, BudgetForm, ExpenseForm, GroceryForm, NoteForm, VoiceForm, ItemForm
from .models import UserProfile, Person, Task, Budget, Expense, Grocery, Item, Note, Voice
from .forms import NewSignupForm, PersonForm, TaskForm, BudgetForm, ExpenseForm, GroceryForm, NoteForm, ItemForm
from .models import UserProfile, Person, Task, Budget, Expense, Grocery, Item, Note
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from datetime import datetime
from django.http import JsonResponse


# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = NewSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                birthday=form.cleaned_data.get('birthday'),
                profile_image=request.FILES.get('profile_image')
            )
            login(request, user)
            return redirect('login')
        else:
            error_message = 'Invalid sign up - try again'
    else:
        form = NewSignupForm()

    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

class PersonList(LoginRequiredMixin, ListView):
    model = Person

    def get_queryset(self):
        return Person.objects.filter(user=self.request.user)

class PersonDetail(LoginRequiredMixin, DetailView):
    model = Person

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

class PersonCreate(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm  # or fields = ['name', 'relationship', 'email', 'contact_date', 'notes']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PersonUpdate(LoginRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm  # or fields = ['name', 'relationship', 'email', 'contact_date', 'notes']

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PersonDelete(LoginRequiredMixin, DeleteView):
    model = Person
    success_url = '/mypeople/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj
    

class TaskList(LoginRequiredMixin, ListView):
    model = Task
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = '/task/'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = '/task/'

class NoteList(LoginRequiredMixin, ListView):
    model = Note
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)
    
class NoteDetail(LoginRequiredMixin, DetailView):
    model = Note

class NoteCreate(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    success_url = '/note/'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

#Budget List View
class BudgetListView(LoginRequiredMixin , ListView):
    model= Budget
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
#Budget Detail View
class BudgetDetailView(LoginRequiredMixin, DetailView):
    model=Budget

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
#Budget Create View
class BudgetCreateView(LoginRequiredMixin, CreateView):
    model= Budget
    form_class= BudgetForm
    success_url= '/budget/'

    def form_valid(self, form):
            form.instance.user = self.request.user
            return super().form_valid(form)

    

class NoteUpdate(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm

class NoteDelete(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = '/note/'
#Budget Update View
class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model= Budget
    form_class= BudgetForm
    success_url= '/budget/'

    def get_queryset(self):
        return Budget.objects.filter(user= self.request.user)
    
#Budget Delete View
class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model=Budget
    success_url='/budget/'

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
#Expense List View
class ExpenseListView(LoginRequiredMixin, ListView):
    model= Expense

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)
    
#Expense Create View
class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model= Expense
    form_class= ExpenseForm
    success_url= '/expense/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
#Expense Update View
class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    success_url = '/expense/'

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

class ItemList(LoginRequiredMixin, ListView):
    model = Item

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = context['object_list']
        locations = set()
        for item in items:
            locations.add(item.location)
        context['unique_locations'] = sorted(locations)
        return context

class ItemDetail(LoginRequiredMixin, DetailView):
    model = Item

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

class ItemCreate(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        new_location = self.request.POST.get('new_location')
        if new_location:
            form.instance.location = new_location
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        new_location = self.request.POST.get('new_location')
        if new_location:
            form.instance.location = new_location
        form.instance.user = self.request.user
        return super().form_valid(form)

class ItemDelete(LoginRequiredMixin, DeleteView):
    model = Item
    success_url = '/items/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

class GroceryList(LoginRequiredMixin, ListView):
    model = Grocery

    def get_queryset(self):
        return Grocery.objects.filter(user=self.request.user)

class GroceryDetail(LoginRequiredMixin, DetailView):
    model = Grocery

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

class GroceryCreate(LoginRequiredMixin, CreateView):
    model = Grocery
    form_class = GroceryForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

#Expense Delete View
class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model= Expense
    success_url= '/expense/'

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

class GroceryUpdate(LoginRequiredMixin, UpdateView):
    model = Grocery
    form_class = GroceryForm

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class GroceryDelete(LoginRequiredMixin, DeleteView):
    model = Grocery
    success_url = '/groceries/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

class VoiceList(LoginRequiredMixin, ListView):
    model = Voice
    def get_queryset(self):
        return Voice.objects.filter(user=self.request.user)
    
class VoiceDetail(LoginRequiredMixin, DetailView):
    model = Voice

class VoiceCreate(LoginRequiredMixin, CreateView):
    model = Voice
    form_class = VoiceForm
    success_url = '/voice/'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class VoiceUpdate(LoginRequiredMixin, UpdateView):
    model = Voice
    form_class = VoiceForm

class VoiceDelete(LoginRequiredMixin, DeleteView):
    model = Voice
    success_url = '/voice/'


def get_tasks():
    total_count = Task.objects.count()
    completed_count = Task.objects.filter(is_completed=True).count()
    completed_percentage = round((completed_count / total_count) * 100) if total_count > 0 else 0

    return {
        'completed_percentage': completed_percentage,
        'total_tasks': total_count,
        'completed_tasks': completed_count,
    }

def get_saving():
    savings = Budget.objects.filter(type='saving')
    expenses = Expense.objects.all()

    total_saving = sum(s.saving_goal for s in savings)
    total_expenses = sum(e.amount for e in expenses)

    if total_saving > total_expenses:
        saving_message = f"🎉 Congrats! You saved {total_saving - total_expenses:.2f} BD this year."
    else:
        saving_message = f"💸 You spent more than you saved by {total_expenses - total_saving:.2f} BD this year."

    return {
        'total_saving': total_saving,
        'total_expenses': total_expenses,
        'saving_message': saving_message,
        'savings_list': savings,
        'expenses_list': expenses,
    }

def get_expense(request):
    if request.method == 'GET':
        expenses = Expense.objects.all()
        data_list = [
            {
                'name': e.name,
                'amount': float(e.amount),
            }
            for e in expenses
        ]
        return JsonResponse({'data': data_list})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_groceries():
    total_items = Grocery.objects.count()
    restocked_items = Grocery.objects.filter(is_restocked=True).count()

    percentage = round((restocked_items / total_items) * 100) if total_items > 0 else 0

    return {
        'total_items': total_items,
        'restocked_items': restocked_items,
        'percentage': percentage
    }


def get_groceries_top(request):
    if request.method == 'GET':
        grocery_counts = Grocery.objects.values('name').annotate(
            restock_count=Count('id', filter=Q(is_restocked=True))
        )

        data_grocery = [
            {
                'name': entry['name'],
                'restock_count': entry['restock_count'],
            }
            for entry in grocery_counts
        ]

        return JsonResponse({'grocery': data_grocery})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_voice():
    current_year = datetime.now().year
    voice_note_count = Voice.objects.filter(created_at__year=current_year).count()
    voice_note_percentage = round((voice_note_count / 365) * 100)

    return {
        'voice_note_count': voice_note_count,
        'voice_note_percentage': voice_note_percentage,
    }
def get_voice_emotion_counts(request):
    if request.method == 'GET':
        emotion_counts = Voice.objects.values('emotion').annotate(
            count=Count('id')
        ).order_by('emotion')

        data = [
            {'emotion': entry['emotion'], 'count': entry['count']}
            for entry in emotion_counts
        ]

        return JsonResponse({'voice_emotions': data})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def achievement_summary(request):
    context = {}
    context.update(get_tasks())
    context.update(get_saving())
    context.update(get_groceries())
    context.update(get_voice())

    return render(request, 'main_app/achievement_list.html', context)
def location_items(request, location):
    items = Item.objects.filter(location=location)
    return render(request, 'main_app/location_items.html', {
        'location': location,
        'items': items,
    })

def send_mail_and_increment(request, pk):
    person = get_object_or_404(Person, pk=pk)
    person.interact_times += 1
    person.save(update_fields=['interact_times'])
    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={person.email}"
    return redirect(gmail_url)

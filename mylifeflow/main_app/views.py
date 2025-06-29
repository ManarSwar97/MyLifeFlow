from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import NewSignupForm, PersonForm, TaskForm, BudgetForm, ExpenseForm, GroceryForm, NoteForm
from .models import UserProfile, Person, Task, Budget, Expense, Grocery, Item, Note
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

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
class NoteDetail(LoginRequiredMixin, DetailView):
    model = Note

class NoteCreate(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    success_url = '/note/'

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
    
class ItemList(LoginRequiredMixin, ListView):
    model = Item

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)

class ItemDetail(LoginRequiredMixin, DetailView):
    model = Item

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

class ItemCreate(LoginRequiredMixin, CreateView):
    model = Item
    fields = ['name', 'location', 'description']

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


class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = Item
    fields = ['name', 'location', 'description'] 

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_form(self, form_class=None):
        # Store the old location before the form is bound and the instance is updated
        self.old_location = self.get_object().location
        return super().get_form(form_class)

    def form_valid(self, form):
        # self.object is the instance being updated, but not yet saved
        new_location = form.cleaned_data['location']
        if self.old_location != new_location:
            if self.old_location:
                if not self.object.movement:
                    self.object.movement = []
                self.object.movement.append(self.old_location)
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

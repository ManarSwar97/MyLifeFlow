from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import NewSignupForm, PersonForm, TaskForm, NoteForm
from .models import UserProfile, Person, Task, Note
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
    form_class = PersonForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PersonUpdate(LoginRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm

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

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class NoteUpdate(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm

class NoteDelete(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = '/note/'

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import NewSignupForm
from .models import UserProfile, Person
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
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

class PersonList(ListView):
    model = Person

class PersonDetail(DetailView):
    model = Person

class PersonCreate(CreateView):
    model = Person
    fields = '__all__'  

class PersonUpdate(UpdateView):
    model = Person
    fields = ['name', 'age'] 

class PersonDelete(DeleteView):
    model = Person
    success_url = '/persons/'
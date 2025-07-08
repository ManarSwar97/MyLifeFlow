from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import NewSignupForm, PersonForm, TaskForm, BudgetForm, ExpenseForm, GroceryForm, NoteForm, VoiceForm, ItemForm
from .models import UserProfile, Person, Task, Budget, Expense, Grocery, Item, Note, Voice, Message
from .forms import NewSignupForm, PersonForm, TaskForm, BudgetForm, ExpenseForm, GroceryForm, NoteForm, ItemForm
from .models import UserProfile, Person, Task, Budget, Expense, Grocery, Item, Note
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from datetime import date
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
import requests
import os 
from dotenv import load_dotenv
load_dotenv()
from .models import Message
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse


# Create your views here.
def home(request):
    return render(request, 'home.html')


@login_required
def dashboard(request):
    #for the weather api 
    if request.user.is_authenticated: #to check if the user authenticated (exist)
        profile = request.user.userprofile #get thee user profile since its contain the latitude and longitude for the location
        lat = profile.latitude
        lon = profile.longitude
    else:
        lat = None
        lon = None

    units = request.GET.get('units', 'metric')
    API_KEY = os.getenv('WEATHER_API_KEY')

    #initialize the weather variable
    weather = None

    #to check if the latitude and longitude is not empty and the api exist
    if lat is not None and lon is not None and API_KEY:
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={API_KEY}'
        
        response = requests.get(url)

        if response.status_code == 200: #in case there was an error and it sends staus 200
            weather = response.json()
        else:
            print("Failed to get weather data:", response.text) #if there is no weather data
    else:
        print("Missing lat/lon or API_KEY") #if latitude and longitude empty and the api does not exist


    #for the quotes api 
    quotes= None
    url = f'https://dummyjson.com/quotes/random'
        
    response = requests.get(url)

    if response.status_code == 200: #in case there was an error and it sends staus 200
            quotes = response.json()
            print(quotes)
    else:
        print("Failed to get quotes data:", response.text) #if there is no weather data


    #for the list some calculations 
    today_tasks= Task.objects.filter(user=request.user, due_date= date.today())
    completed= today_tasks.filter(is_completed=True).count()
    total= today_tasks.count()
    percentage= int((completed/total)*100) if total else 0
    pending= total- completed

    budget_list = Budget.objects.filter(user=request.user)
    person_list = Person.objects.filter(user=request.user)
    total_interacts = person_list.aggregate(total=Sum('interact_times'))['total'] or 0
    
    #for grocieries 
    next_day= timezone.localdate() + timedelta(days=1)
    all_groceries = Grocery.objects.filter(user=request.user, is_restocked=False)
    grocery_list = [g for g in all_groceries if g.next_restock <= next_day]


    #for budgets
    budgets = [
        {
            'budget': budget,
            'spent': budget.expense_set.aggregate(total_spent=Sum('amount'))['total_spent'] or 0,
            'today_spent': budget.expense_set.filter(created_at__date=timezone.now().date()).aggregate(today_total=Sum('amount'))['today_total'] or 0,
            'remaining': float(budget.total_amount) - float(budget.expense_set.aggregate(total_spent=Sum('amount'))['total_spent'] or 0),
            'daily_limit': budget.daily_limit(),
            'remaining_daily_limit': max(budget.daily_limit() - (budget.expense_set.filter(created_at__date=timezone.now().date()).aggregate(today_total=Sum('amount'))['today_total'] or 0), 0),
            'expenses': budget.expense_set.order_by('-created_at')
        }
        for budget in budget_list
    ]


    return render(request, 'dashboard.html', {
        'task_list': today_tasks,
        'grocery_list': grocery_list,
        'budget_list': budget_list,
        'budgets':budgets,
        'person_list': person_list,
        'weather': weather,
        'units': units,
        'quotes': quotes,
        'completed': completed,
        'pending': pending,
        'percentage': percentage,
        'interact_times': total_interacts,
        'restock_count': len(grocery_list), 
    })



def about(request):
    return render(request, 'about.html')

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = NewSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            #to get them from the inputs
            latitude = float(request.POST.get('latitude', 0.0))
            longitude = float(request.POST.get('longitude', 0.0))

            UserProfile.objects.create(
                user=user,
                birthday=form.cleaned_data.get('birthday'),
                profile_image=request.FILES.get('profile_image'),
                latitude=latitude,
                longitude= longitude
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
        registered_emails = set(User.objects.values_list('email', flat=True))
        persons= Person.objects.filter(user=self.request.user)
        for person in persons:
            person.is_registered_user = person.email in registered_emails
        return persons

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

def dashboard_add_task(request):
    if request.method == 'POST':
        #strip() string methed to delete spaces
        title = request.POST.get('title', '').strip()
        if title:
            Task.objects.create(
                title=title,
                description='',
                due_date=date.today(),
                is_completed=False,
                user=request.user
            )
    return redirect('home')  
    

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
    form_class = ItemForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # optional, safe to keep
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_choices'] = self.get_form().existing_locations
        return context


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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        budget_id = self.request.GET.get('budget_id')
        if budget_id:
            initial['budget'] = budget_id
        return initial
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

def dashboard_add_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        budget_id = request.POST.get('budget_id')

        budget = Budget.objects.get(id=budget_id, user=request.user)

#adjust the default values for the dashboard form
        Expense.objects.create(
            name=title,
            amount=amount,
            frequency='one-time',  
            budget=budget,
            user=request.user
        )
        return redirect('home') 
    

#Expense Update View
class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    success_url = '/expense/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        budget_id = self.request.GET.get('budget_id')
        if budget_id:
            initial['budget'] = budget_id
        return initial

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        item = form.instance
        old_location = self.get_object().location
        new_location = self.request.POST.get('new_location') or form.cleaned_data.get('location')

        # Update movement if the location changed
        if old_location != new_location:
            item.movement = item.movement or []
            item.movement.append(old_location)
            item.location = new_location

        item.user = self.request.user
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


def get_tasks(user):
    total_count = Task.objects.count()
    completed_count = Task.objects.filter(user=user, is_completed=True).count()
    completed_percentage = round((completed_count / total_count) * 100) if total_count > 0 else 0

    return {
        'completed_percentage': completed_percentage,
        'total_tasks': total_count,
        'completed_tasks': completed_count,
    }


def get_saving(user):
    savings = Budget.objects.filter(user=user, type='saving')
    expenses = Expense.objects.filter(user=user)

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

@login_required
def get_expense(request):
    user = request.user
    if request.method == 'GET':
        expenses = Expense.objects.filter(user=user)
        data_list = [
            {
                'name': e.name,
                'amount': float(e.amount),
            }
            for e in expenses
        ]
        return JsonResponse({'data': data_list})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_groceries(user):
    total_items = Grocery.objects.count()
    restocked_items = Grocery.objects.filter(user=user, is_restocked=True).count()

    percentage = round((restocked_items / total_items) * 100) if total_items > 0 else 0

    return {
        'total_items': total_items,
        'restocked_items': restocked_items,
        'percentage': percentage
    }

@login_required
def get_groceries_top(request):
    user = request.user
    if request.method == 'GET':
        grocery_counts = Grocery.objects.filter(user=user, is_restocked=True).values('name').annotate(restock_count=Count('id'))

        data_grocery = [
            {
                'name': entry['name'],
                'restock_count': entry['restock_count'],
            }
            for entry in grocery_counts
        ]

        return JsonResponse({'grocery': data_grocery})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_voice(user):
    current_year = datetime.now().year
    voice_note_count = Voice.objects.filter(user=user, created_at__year=current_year).count()
    voice_note_percentage = round((voice_note_count / 365) * 100)

    return {
        'voice_note_count': voice_note_count,
        'voice_note_percentage': voice_note_percentage,
    }

@login_required
def get_voice_emotion_counts(request):
    user = request.user
    if request.method == 'GET':
        emotion_counts = Voice.objects.filter(user=user).values('emotion').annotate(count=Count('id')).order_by('emotion')
        data = [
            {'emotion': entry['emotion'], 'count': entry['count']}
            for entry in emotion_counts
        ]

        return JsonResponse({'voice_emotions': data})

    return JsonResponse({'error': 'Invalid request method'}, status=400)




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

@login_required
def achievement_summary(request):
    user = request.user
    context = {}
    context.update(get_tasks(user))
    context.update(get_saving(user))
    context.update(get_groceries(user))
    context.update(get_voice(user))
    top_people = Person.objects.order_by('-interact_times')[:5]
    context['top_people'] = top_people
    return render(request, 'main_app/achievement_list.html', context)


#for messages part
@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '') 
    users = User.objects.exclude(id=request.user.id) 
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))  

    chats = chats.order_by('timestamp') 
    user_last_messages = []

    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Sort user_last_messages by the timestamp of the last_message in descending order
    user_last_messages.sort(
    key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.make_aware(datetime.min),
    reverse=True
)

    return render(request, 'chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query 
    })

@login_required
def send_message(request, pk):
    person = get_object_or_404(Person, pk=pk, user=request.user)
    try:
        matched_user = User.objects.get(email=person.email)
        # You can redirect to an internal chat room, message form, etc.
        return redirect('start_chat', user_id=matched_user.id)
    except User.DoesNotExist:
        messages.error(request, "This person is not a registered user.")
        return redirect('person_index')

@login_required
def start_chat(request, user_id):
    matched_user = get_object_or_404(User, pk=user_id)
    # Redirect using the username as room name (used in chat_room)
    return redirect('chat', room_name=matched_user.username)

@login_required
def profile(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {
        'profile':profile
    })

@login_required
def task_list_search(request):
    query = request.GET.get('q', '')
    if query:
        task_list = Task.objects.filter(user=request.user, title__icontains=query)
    else:
        task_list = Task.objects.filter(user=request.user)

    print("RESULTS:", task_list)

    context = {
        'task_list': task_list,
        'query': query,
    }
    return render(request, 'main_app/task_list.html', context)
@login_required
def person_list_search(request):
    query = request.GET.get('q', '')
    if query:
        person_list = Person.objects.filter(user=request.user, name__icontains=query)
    else:
        person_list = Person.objects.filter(user=request.user)

    print("RESULTS:", person_list)

    context = {
        'person_list': person_list,
        'query': query,
    }
    return render(request, 'main_app/person_list.html', context)

@login_required
def item_list_search(request):
    query = request.GET.get('q', '')
    if query:
        item_list = Item.objects.filter(user=request.user, name__icontains=query)
    else:
        item_list = Item.objects.filter(user=request.user)

    print("RESULTS:", item_list)

    context = {
        'item_list': item_list,
        'query': query,
    }
    return render(request, 'main_app/item_list.html', context)

@login_required
def grocery_list_search(request):
    query = request.GET.get('q', '')
    if query:
        grocery_list = Grocery.objects.filter(user=request.user, name__icontains=query)
    else:
        grocery_list = Grocery.objects.filter(user=request.user)

    print("RESULTS:", grocery_list)

    context = {
        'grocery_list': grocery_list,
        'query': query,
    }
    return render(request, 'main_app/grocery_list.html', context)


@login_required
def budget_list_search(request):
    query = request.GET.get('q', '')
    if query:
        budget_list = Budget.objects.filter(user=request.user, name__icontains=query)
    else:
        budget_list = Budget.objects.filter(user=request.user)

    print("RESULTS:", budget_list)

    context = {
        'budget_list': budget_list,
        'query': query,
    }
    return render(request, 'main_app/budget_list.html', context)

@login_required
def expense_list_search(request):
    query = request.GET.get('q', '')
    if query:
        expense_list = Expense.objects.filter(user=request.user, name__icontains=query)
    else:
        expense_list = Expense.objects.filter(user=request.user)

    print("RESULTS:", expense_list)

    context = {
        'expense_list': expense_list,
        'query': query,
    }
    return render(request, 'main_app/expense_list.html', context)


@login_required
def note_list_search(request):
    query = request.GET.get('q', '')
    if query:
        note_list = Note.objects.filter(user=request.user, title__icontains=query)
    else:
        note_list = Note.objects.filter(user=request.user)

    print("RESULTS:", note_list)

    context = {
        'note_list': note_list,
        'query': query,
    }
    return render(request, 'main_app/note_list.html', context)


@login_required
def voice_list_search(request):
    query = request.GET.get('q', '')
    if query:
        voice_list = Voice.objects.filter(user=request.user, title__icontains=query)
    else:
        voice_list = Voice.objects.filter(user=request.user)

    print("RESULTS:", voice_list)

    context = {
        'voice_list': voice_list,
        'query': query,
    }
    return render(request, 'main_app/voice_list.html', context)
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='home'),
    path('about/', views.about, name='about'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/signup/', views.signup, name='signup'),

# My People feature URLs
    path('mypeople/', views.PersonList.as_view(), name='person_index'),
    path('mypeople/<int:pk>/', views.PersonDetail.as_view(), name='person_detail'),
    path('mypeople/create/', views.PersonCreate.as_view(), name='person_create'),
    path('mypeople/<int:pk>/update/', views.PersonUpdate.as_view(), name='person_update'),
    path('mypeople/<int:pk>/delete/', views.PersonDelete.as_view(), name='person_delete'),
# Daily Tasks feature URLs
    path('task/', views.TaskList.as_view(), name='task_index'),
    path('task/<int:pk>/', views.TaskDetail.as_view(), name='task_detail'),
    path('task/create/', views.TaskCreate.as_view(), name='task_create'),
    path('task/<int:pk>/update/', views.TaskUpdate.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', views.TaskDelete.as_view(), name='task_delete'),
# Journal feature URLs
    path('note/', views.NoteList.as_view(), name='note_index'),
    path('note/<int:pk>/', views.NoteDetail.as_view(), name='note_detail'),
    path('note/create/', views.NoteCreate.as_view(), name='note_create'),
    path('note/<int:pk>/update/', views.NoteUpdate.as_view(), name='note_update'),
    path('note/<int:pk>/delete/', views.NoteDelete.as_view(), name='note_delete'),

#Budget feature URLs
    path('budget/', views.BudgetListView.as_view(), name='budget_list'),
    path('budget/<int:pk>/', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('budget/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budget/<int:pk>/update/', views.BudgetUpdateView.as_view(), name='budget_update'),
    path('budget/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),

#Expense feature URLs
    path('expense/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expense/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expense/<int:pk>/update/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expense/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),

# Item feature URLs
    path('items/', views.ItemList.as_view(), name='item_index'),
    path('items/create/', views.ItemCreate.as_view(), name='item_create'),
    path('items/<int:pk>/', views.ItemDetail.as_view(), name='item_detail'),
    path('items/<int:pk>/update/', views.ItemUpdate.as_view(), name='item_update'),
    path('items/<int:pk>/delete/', views.ItemDelete.as_view(), name='item_delete'),

# Grocery feature URLs
    path('groceries/', views.GroceryList.as_view(), name='grocery_index'),
    path('groceries/create/', views.GroceryCreate.as_view(), name='grocery_create'),
    path('groceries/<int:pk>/', views.GroceryDetail.as_view(), name='grocery_detail'),
    path('groceries/<int:pk>/update/', views.GroceryUpdate.as_view(), name='grocery_update'),
    path('groceries/<int:pk>/delete/', views.GroceryDelete.as_view(), name='grocery_delete'),
]
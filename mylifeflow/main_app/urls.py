from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/signup/', views.signup, name='signup'),

# My People feature URLs
    path('mypeople/', views.PersonList.as_view(), name='people_index'),
    path('mypeople/<int:pk>/', views.PersonDetail.as_view(), name='people_detail'),
    path('mypeople/create/', views.PersonCreate.as_view(), name='people_create'),
    path('mypeople/<int:pk>/update/', views.PersonUpdate.as_view(), name='people_update'),
    path('mypeople/<int:pk>/delete/', views.PersonDelete.as_view(), name='people_delete')
]

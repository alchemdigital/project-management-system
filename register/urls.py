from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'register'

urlpatterns = [
    path('new-user/', views.register, name='new-user'),
    path('new-company/', views.newCompany, name='new-company'),
    path('users/', views.usersView, name='users'),
    path('users/profile', views.profile, name='profile'),
    path('users/<int:profile_id>/', views.user_view, name='user'),
    path('', include('django.contrib.auth.urls')),
]


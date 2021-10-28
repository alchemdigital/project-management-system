from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'register'

urlpatterns = [
    path('new-user/', views.register, name='new-user'),
    path('new-company/', views.new_company, name='new-company'),
    path('companies/', views.companies, name='companies'),
    path('edit-company/<int:company_id>/', views.edit_company, name='edit_company'),
    path('update-company/', views.update_company, name='update_company'),
    path('delete-company/<int:company_id>/', views.delete_company, name='delete_company'),
    path('users/', views.users, name='users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('update-user/', views.update_user, name='update_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    # path('users/profile', views.profile, name='profile'),
    # path('users/<int:profile_id>/', views.user_view, name='user'),
    path('', include('django.contrib.auth.urls')),
    path('attendance/', views.attendance, name='attendance'),
    path('add-attendance/', views.add_attendance, name='add_attendance'),
    path('admin/', views.admin_register, name='admin_register'),
]


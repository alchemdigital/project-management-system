from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'projects'

urlpatterns = [
    path('', views.projects, name='projects'),
    path('new-project/', views.new_project, name='new-project'),
    path('new-task/', views.new_task, name='new-task'),
    path('new-checklist/', views.new_checklist, name='new-checklist'),
]
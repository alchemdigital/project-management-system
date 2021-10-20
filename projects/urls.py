from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'projects'

urlpatterns = [
    path('', views.projects, name='projects'),
    # Project CRUD - start
    path('new-project/', views.new_project, name='new-project'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:company_id>/', views.projects, name='projects'),
    path('edit-project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('update-project/', views.update_project, name='update_project'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    # Project CRUD - end
    # Task CRUD - start
    path('new-task/', views.new_task, name='new-task'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/<int:project_id>/', views.tasks, name='tasks'),
    path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('update-task/', views.update_task, name='update_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    # Task CRUD - end
    # Checklist CRUD - start
    path('new-checklist/', views.new_checklist, name='new-checklist'),
    path('checklists/', views.checklists, name='checklists'),
    path('checklists/<int:task_id>', views.checklists, name='checklists'),
    path('edit-checklist/<int:checklist_id>/', views.edit_checklist, name='edit_checklist'),
    path('update-checklist/', views.update_checklist, name='update_checklist'),
    path('delete-checklist/<int:checklist_id>/', views.delete_checklist, name='delete_checklist'),
    # Checklist CRUD - end
    path('download-import-sample', views.download_import_sample, name='download_import_sample'),
    path('import-tasks', views.import_tasks, name='import_tasks'),
    path('export-tasks', views.export_tasks, name='export_tasks'),
    path('last-worked-employee/<int:project_id>', views.last_worked_employee, name='last_worked_employee')
]
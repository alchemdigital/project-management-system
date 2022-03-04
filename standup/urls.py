from django.urls import path
from . import views

app_name = 'standup'

urlpatterns = [
    path('', views.index, name="standup"),
    path('employee-select', views.employee_select, name="employee_select"),
    path('new-standup/<int:employee_id>', views.new_standup, name="new_standup"),
    path('view-standup/<int:employee_id>', views.view_standup, name="view_standup"),
    # path('get-project-field', views.project_field, name='project-field')
]

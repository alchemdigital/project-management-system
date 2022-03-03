import django_filters
from .models import *

def filter_users_by_admin(request):
	if request is None:
		return User.objects.none()
	return User.objects.filter(admin=request.user.admin)

def filter_projects_by_admin(request):
	if request is None:
		return Project.objects.none()
	return Project.objects.filter(admin=request.user.admin)

class TaskFilter(django_filters.FilterSet):
	employee = django_filters.ModelChoiceFilter(queryset=filter_users_by_admin)
	project = django_filters.ModelChoiceFilter(queryset=filter_projects_by_admin)
	start_date = django_filters.DateFromToRangeFilter(
		widget=django_filters.widgets.RangeWidget(attrs={'placeholder': 'YYYY/MM/DD', 'type': 'date'}))
	status = django_filters.MultipleChoiceFilter(choices=status)
	created = django_filters.ModelChoiceFilter(queryset=filter_users_by_admin)

	class Meta:
		model = Task
		fields = ('project', 'employee', 'task_name', 'status', 'deadline',
		          'start_date', 'estimate_hours', 'hours', 'description', 'created')

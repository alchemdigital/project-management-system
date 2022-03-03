import django_filters
from .models import *
from django.db.models import Q

def filter_users_by_admin(request):
	if request is None:
		return User.objects.none()
	return User.objects.filter(admin=request.user.admin).filter(groups__name__in=['admin', 'project_manager', 'employee'])

def filter_projects_by_admin(request):
	if request is None:
		return Project.objects.none()
	return Project.objects.filter(admin=request.user.admin)

class TaskFilter(django_filters.FilterSet):
	employee = django_filters.ModelChoiceFilter(queryset=filter_users_by_admin, label='Assigned To')
	project = django_filters.ModelChoiceFilter(queryset=filter_projects_by_admin)
	start_date = django_filters.DateFromToRangeFilter(
		widget=django_filters.widgets.RangeWidget(attrs={'placeholder': 'YYYY/MM/DD', 'type': 'date'}))
	status = django_filters.MultipleChoiceFilter(choices=status)
	created = django_filters.ModelChoiceFilter(
		queryset=filter_users_by_admin, label='Assigned By')
	search_all = django_filters.CharFilter(method='task_search', label='Search')

	class Meta:
		model = Task
		fields = ('search_all', 'project', 'employee', 'status', 'deadline',
		          'start_date', 'created')

	def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
		super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
		self.filters['search_all'].field.widget.attrs.update({'class': 'form-control'})
		self.filters['created'].field.widget.attrs.update({'class': 'form-control'})
		self.filters['status'].field.widget.attrs.update({'class': 'form-control'})
		self.filters['start_date'].field.widget.attrs.update({'class': 'form-control'})
		self.filters['project'].field.widget.attrs.update({'class': 'form-control'})
		self.filters['employee'].field.widget.attrs.update({'class': 'form-control'})

	def task_search(self, queryset, name, value):
		return queryset.filter(Q(task_name__icontains=value) | Q(description__icontains=value))

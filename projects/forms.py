from django import forms
from django.utils.text import slugify
from .models import Task
from .models import Project
from .models import Checklist
from register.models import Company
from django.contrib.auth import get_user_model
User = get_user_model()
from dal import autocomplete
import datetime
from django.forms import DateTimeField

status = (
    ('1', 'Yet to Start'),
    ('2', 'In Progress'),
    ('3', 'QC Pending'),
    ('4', 'Completed'),
)

class ProjectRegistrationForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'company', 'description')

    def save(self, commit=True, instance=None):
        project = super(ProjectRegistrationForm, self).save(commit=False)
        project.name = self.cleaned_data['name']
        project.company = self.cleaned_data['company']
        project.description = self.cleaned_data['description']
        project.slug = slugify(str(self.cleaned_data['name']))
        if self.instance.pk == None:
            project.admin = self.user.admin
            project.created = self.user
        else:
            project.admin = self.instance.admin
            project.created = self.instance.updated
        project.updated = self.user
        project.save()
        return project

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user')
        super(ProjectRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(max_length=80)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Project Name *'
        self.fields['company'] = forms.ModelChoiceField(queryset=Company.objects.filter(admin=self.user.admin), widget=autocomplete.ModelSelect2(url='/projects/company-autocomplete'), empty_label='Select a Company*')
        self.fields['company'].widget.attrs['class'] = 'form-control'
        self.fields['description'] = forms.CharField(widget=forms.Textarea, required=False)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Type here the project description...'

class TaskRegistrationForm(forms.ModelForm):
    forms.DateInput.input_type = 'date'
    forms.DateTimeInput.input_type = 'datetime-local'
    # deadline = DateTimeField(input_formats=['%Y-%m-%dT%H:%M'])
    # forms.DateTimeInput.input_formats = '%Y-%m-%d %H:%M:%S'

    class Meta:
        model = Task
        fields = ('project', 'employee', 'task_name', 'status', 'deadline', 'start_date', 'estimate_hours', 'hours', 'description')

    def save(self, commit=True):
        task = super(TaskRegistrationForm, self).save(commit=False)
        task.project = self.cleaned_data['project']
        task.task_name = self.cleaned_data['task_name']
        task.status = self.cleaned_data['status']
        task.employees = self.cleaned_data['employee']
        if self.instance.pk == None:
            task.admin = self.user.admin
            task.created = self.user
        else:
            task.admin = self.instance.admin
            task.created = self.instance.created
        task.updated = self.user
        task.save()
        return task

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user')
        super(TaskRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['project'] = forms.ModelChoiceField(queryset=Project.objects.filter(admin=self.user.admin), widget=autocomplete.ModelSelect2(url='/projects/project-autocomplete'), empty_label='Select a Project *')
        self.fields['project'].widget.attrs['class'] = 'form-control'
        self.fields['employee'] = forms.ModelChoiceField(queryset=User.objects.filter(admin=self.user.admin, groups__in=(1, 2,3)), widget=autocomplete.ModelSelect2(url='/projects/employee-autocomplete'), empty_label='Select an employee', required=False)
        self.fields['employee'].widget.attrs['class'] = 'form-control'
        self.fields['task_name'] = forms.CharField(max_length=80)
        self.fields['task_name'].widget.attrs['class'] = 'form-control'
        self.fields['task_name'].widget.attrs['placeholder'] = 'Name *'
        self.fields['status'] = forms.ChoiceField(choices=status, required=False)
        self.fields['status'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['placeholder'] = 'Status'
        self.fields['deadline'] = forms.DateTimeField(required=False, input_formats=['%Y-%m-%dT%H:%M'])
        self.fields['deadline'].widget.attrs['class'] = 'form-control'
        self.fields['deadline'].widget.attrs['placeholder'] = 'Deadline'
        self.fields['start_date'] = forms.DateTimeField(required=False, initial=datetime.datetime.now())
        self.fields['start_date'].widget.attrs['class'] = 'form-control'
        self.fields['start_date'].widget.attrs['placeholder'] = 'Start Date'
        self.fields['estimate_hours'] = forms.IntegerField(required=False, initial=0)
        self.fields['estimate_hours'].widget.attrs['class'] = 'form-control'
        self.fields['estimate_hours'].widget.attrs['placeholder'] = 'Estimate Hours'
        self.fields['hours'] = forms.IntegerField(required=False, initial=0)
        self.fields['hours'].widget.attrs['class'] = 'form-control'
        self.fields['hours'].widget.attrs['placeholder'] = 'Hours'
        self.fields['description'] = forms.CharField(widget=forms.Textarea, required=False)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Description'

class ChecklistRegistrationForm(forms.ModelForm):

    class Meta:
        model = Checklist
        fields = ('task', 'checklist_name', 'status')


    def save(self, commit=True):
        checklist = super(ChecklistRegistrationForm, self).save(commit=False)
        checklist.task = self.cleaned_data['task']
        checklist.checklist_name = self.cleaned_data['checklist_name']
        checklist.status = self.cleaned_data['status']
        if self.instance.pk == None:
            checklist.admin = self.user.admin
            checklist.created = self.user
        else:
            checklist.admin = self.instance.admin
            checklist.created = self.instance.created
        checklist.user = self.user
        checklist.updated = self.user
        checklist.save()
        return checklist


    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user')
        super(ChecklistRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['task'] = forms.ModelChoiceField(queryset=Task.objects.filter(admin=self.user.admin), widget=autocomplete.ModelSelect2(url='/projects/task-autocomplete'), empty_label='Select a Task *')
        self.fields['task'].widget.attrs['class'] = 'form-control'
        self.fields['checklist_name'] = forms.CharField()
        self.fields['checklist_name'].widget.attrs['class'] = 'form-control'
        self.fields['checklist_name'].widget.attrs['placeholder'] = 'Name *'
        self.fields['status'] = forms.ChoiceField(choices=status, required=False)
        self.fields['status'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['placeholder'] = 'Status'

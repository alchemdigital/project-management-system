from django import forms
from django.utils.text import slugify
from .models import Task
from .models import Project
from .models import Checklist
from register.models import Company
from django.contrib.auth.models import User

status = (
    ('1', 'Yet to Start'),
    ('2', 'In Progress'),
    ('3', 'QC Pending'),
    ('4', 'Completed'),
)

class ProjectRegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=80)
    # slug = forms.SlugField('shortcut')
    company = forms.ModelChoiceField(queryset=Company.objects.all(), empty_label='Select a Company *')
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Project
        fields = '__all__'


    def save(self, commit=True):
        Project = super(ProjectRegistrationForm, self).save(commit=False)
        Project.name = self.cleaned_data['name']
        Project.company = self.cleaned_data['company']
        Project.description = self.cleaned_data['description']
        Project.slug = slugify(str(self.cleaned_data['name']))
        Project.save()
        return Project

    def __init__(self, *args, **kwargs):
        super(ProjectRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Project Name *'
        self.fields['company'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Type here the project description...'

class TaskRegistrationForm(forms.ModelForm):
    forms.DateInput.input_type="date"

    project = forms.ModelChoiceField(queryset=Project.objects.all(), empty_label='Select a Project *')
    employee = forms.ModelChoiceField(queryset=User.objects.filter(groups=3), empty_label='Select an employee', required=False)
    task_name = forms.CharField(max_length=80)
    status = forms.ChoiceField(choices=status, required=False)
    deadline = forms.DateField(required=False)
    start_date = forms.DateField(required=False)
    hours = forms.IntegerField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Task
        fields = '__all__'

    def save(self, commit=True):
        task = super(TaskRegistrationForm, self).save(commit=False)
        task.project = self.cleaned_data['project']
        task.task_name = self.cleaned_data['task_name']
        task.status = self.cleaned_data['status']
        task.employees = self.cleaned_data['employee']
        task.save()
        return task


    def __init__(self, *args, **kwargs):
        super(TaskRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['project'].widget.attrs['class'] = 'form-control'
        self.fields['employee'].widget.attrs['class'] = 'form-control'
        self.fields['task_name'].widget.attrs['class'] = 'form-control'
        self.fields['task_name'].widget.attrs['placeholder'] = 'Name *'
        self.fields['status'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['placeholder'] = 'Status'
        self.fields['deadline'].widget.attrs['class'] = 'form-control'
        self.fields['deadline'].widget.attrs['placeholder'] = 'Deadline'
        self.fields['start_date'].widget.attrs['class'] = 'form-control'
        self.fields['start_date'].widget.attrs['placeholder'] = 'Start Date'
        self.fields['hours'].widget.attrs['class'] = 'form-control'
        self.fields['hours'].widget.attrs['placeholder'] = 'Hours'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Description'

class ChecklistRegistrationForm(forms.ModelForm):
    task = forms.ModelChoiceField(queryset=Task.objects.all(), empty_label='Select a Task *')
    checklist_name = forms.CharField()
    status = forms.ChoiceField(choices=status, required=False)

    class Meta:
        model = Checklist
        fields = '__all__'


    def save(self, commit=True):
        checklist = super(ChecklistRegistrationForm, self).save(commit=False)
        checklist.task = self.cleaned_data['task']
        checklist.checklist_name = self.cleaned_data['checklist_name']
        checklist.status = self.cleaned_data['status']
        checklist.save()
        return checklist


    def __init__(self, *args, **kwargs):
        super(ChecklistRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['task'].widget.attrs['class'] = 'form-control'
        self.fields['checklist_name'].widget.attrs['class'] = 'form-control'
        self.fields['checklist_name'].widget.attrs['placeholder'] = 'Name *'
        self.fields['status'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['placeholder'] = 'Status'

from dataclasses import fields
from django import forms
from .models import Standup, Task as StandupTask
from projects.models import Project
from django.contrib.auth import get_user_model
User = get_user_model()
from dal import autocomplete


class StandupRegistrationForm(forms.ModelForm):
    class Meta:
        model = Standup
        fields = ('is_any_issue', 'employee')
    
    def save(self, commit=True):
        standup = super(StandupRegistrationForm, self).save(commit=False)
        standup.employee = self.cleaned_data['employee']
        standup.is_any_issue = self.cleaned_data['is_any_issue']
        if self.instance.pk == None:
            standup.admin = self.user.admin
        else:
            standup.admin = self.instance.admin
        standup.save()
        return standup
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user')
        super(StandupRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['project'] = forms.ModelChoiceField(queryset=Project.objects.filter(admin=self.user.admin), widget=autocomplete.ModelSelect2(url='/projects/project-autocomplete'), empty_label='Select a Project *')
        self.fields['project'].widget.attrs['class'] = 'form-control'
        self.fields['employee'] = forms.ModelChoiceField(queryset=User.objects.filter(admin=self.user.admin, groups__in=(
            1, 2, 3)), widget=autocomplete.ModelSelect2(url='/projects/employee-autocomplete'), empty_label='Select an employee', required=False)
        self.fields['employee'].widget.attrs['class'] = 'form-control'
        self.fields['is_any_issue'] = forms.CharField(widget=forms.Textarea)
        self.fields['is_any_issue'].widget.attrs['class'] = 'form-control'

class StandupTaskRegistration(forms.ModelForm):
    class Meta:
        model = StandupTask
        fields = ('standup', 'task')
    
    def save(self, commit=True):
        standup_task = super(StandupTaskRegistration, self).save(commit=False)
        standup_task.standup = self.cleaned_data['standup']
        standup_task.task = self.cleaned_data['task']
        standup_task.save()
        return standup_task

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user')
        super(StandupTaskRegistration, self).__init__(*args, **kwargs)
        


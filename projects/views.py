from django.shortcuts import render
from django.db.models import Avg
from register.models import Project
from projects.models import Task
from projects.forms import ProjectRegistrationForm, TaskRegistrationForm, ChecklistRegistrationForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q


def is_project_manager(user):
    return user.groups.filter(name='project_manager').exists()

def is_admin(user):
    return user.groups.filter(name='admin').exists()

def is_pm_or_admin(user):
    return user.groups.filter(Q(name='project_manager') | Q(name='admin')).exists()

# Create your views here.
@user_passes_test(is_pm_or_admin)
def projects(request):
    projects = Project.objects.all()
    avg_projects = Project.objects.all()
    tasks = Task.objects.all()
    context = {
        'avg_projects' : avg_projects,
        'projects' : projects,
        'tasks' : tasks,
        'overdue_tasks' : (),
    }
    return render(request, 'projects/projects.html', context)

@user_passes_test(is_pm_or_admin)
def new_task(request):
    if request.method == 'POST':
        form = TaskRegistrationForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            form.save()
            created = True
            context = {
                'created': created,
                'form': form,
            }
            return render(request, 'projects/new_task.html', context)
        else:
            return render(request, 'projects/new_task.html', context)
    else:
        form = TaskRegistrationForm()
        context = {
            'form': form,
        }
        return render(request,'projects/new_task.html', context)

@user_passes_test(is_pm_or_admin)
def new_project(request):
    if request.method == 'POST':
        form = ProjectRegistrationForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            form.save()
            created = True
            form = ProjectRegistrationForm()
            context = {
                'created': created,
                'form': form,
            }
            return render(request, 'projects/new_project.html', context)
        else:
            return render(request, 'projects/new_project.html', context)
    else:
        form = ProjectRegistrationForm()
        context = {
            'form': form,
        }
        return render(request,'projects/new_project.html', context)

def new_checklist(request):
    if request.method == 'POST':
        form = ChecklistRegistrationForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            form.save()
            created = True
            form = ChecklistRegistrationForm()
            context = {
                'form': form,
                'created': created,
            }
            return render(request, 'projects/new_checklist.html', context)
        else:
            return render(request, 'projects/new_checklist.html', context)
    else:
        form = ChecklistRegistrationForm()
        context = {
            'form': form,
        }
        return render(request,'projects/new_checklist.html', context)
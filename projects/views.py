from django.shortcuts import render
from django.db.models import Avg
from projects.models import Project, Task, Checklist
from projects.forms import ProjectRegistrationForm, TaskRegistrationForm, ChecklistRegistrationForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect


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
            return render(request, 'projects/project_form.html', context)
    else:
        form = ProjectRegistrationForm()
        context = {
            'form': form,
        }
        return render(request,'projects/project_form.html', context)

@user_passes_test(is_pm_or_admin)
def projects(request):
    projects = Project.objects.all()
    paginated_projects = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_projects.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/projects.html', context)

@user_passes_test(is_pm_or_admin)
def edit_project(request, project_id):
    project = Project.objects.get(id=project_id)
    form = ProjectRegistrationForm(instance=project)
    context = {
        'id': project.id,
        'form': form,
        'edit': True
    }
    return render(request, 'projects/project_form.html', context)

@user_passes_test(is_pm_or_admin)
def update_project(request):
    id = request.POST.get('id')
    instance = Project.objects.get(id = id)
    form = ProjectRegistrationForm(request.POST, instance=instance)
    context = { 'form': form, 'id': instance.id, 'edit': True}
    if form.is_valid():
        form.save()
        context['updated'] = True
    return render(request, 'projects/project_form.html', context)

@user_passes_test(is_pm_or_admin)
def delete_project(request, project_id):
    project = Project.objects.get(id=project_id)
    project.delete()
    return redirect('projects:projects')

# Task CRUD - start
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
            return render(request, 'projects/task_form.html', context)
        else:
            return render(request, 'projects/task_form.html', context)
    else:
        form = TaskRegistrationForm()
        context = {
            'form': form,
        }
        return render(request,'projects/task_form.html', context)

@user_passes_test(is_pm_or_admin)
def tasks(request):
    tasks = Task.objects.all()
    paginated_tasks = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_tasks.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/tasks.html', context)

@user_passes_test(is_pm_or_admin)
def edit_task(request, task_id):
    task = Task.objects.get(id=task_id)
    form = TaskRegistrationForm(instance=task)
    context = {
        'id': task.id,
        'form': form,
        'edit': True
    }
    return render(request, 'projects/task_form.html', context)

@user_passes_test(is_pm_or_admin)
def update_task(request):
    id = request.POST.get('id')
    instance = Task.objects.get(id = id)
    form = TaskRegistrationForm(request.POST, instance=instance)
    context = { 'form': form, 'id': instance.id, 'edit': True}
    if form.is_valid():
        form.save()
        context['updated'] = True
    return render(request, 'projects/task_form.html', context)

@user_passes_test(is_pm_or_admin)
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.delete()
    return redirect('projects:tasks')
# Task CRUD - end

#Checklist CRUD - start
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
            return render(request, 'projects/checklist_form.html', context)
        else:
            return render(request, 'projects/checklist_form.html', context)
    else:
        form = ChecklistRegistrationForm()
        context = {
            'form': form,
        }
        return render(request,'projects/checklist_form.html', context)

def checklists(request):
    checklists = Checklist.objects.all()
    paginated_checklists = Paginator(checklists, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_checklists.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/checklists.html', context)

def edit_checklist(request, checklist_id):
    checklist = Checklist.objects.get(id=checklist_id)
    form = ChecklistRegistrationForm(instance=checklist)
    context = {
        'id': checklist.id,
        'form': form,
        'edit': True
    }
    return render(request, 'projects/checklist_form.html', context)

def update_checklist(request):
    id = request.POST.get('id')
    instance = Checklist.objects.get(id = id)
    form = ChecklistRegistrationForm(request.POST, instance=instance)
    context = { 'form': form, 'id': instance.id, 'edit': True}
    if form.is_valid():
        form.save()
        context['updated'] = True
    return render(request, 'projects/checklist_form.html', context)

def delete_checklist(request, checklist_id):
    checklist = Checklist.objects.get(id=checklist_id)
    checklist.delete()
    return redirect('projects:checklists')
#Checklist CRUD - end
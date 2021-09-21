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
def new_project(request):
    if request.method == 'POST':
        form = ProjectRegistrationForm(request.POST, use_required_attribute=False)
        context = {'form': form}
        if form.is_valid():
            form.save()
            created = True
            form = ProjectRegistrationForm(use_required_attribute=False)
            context = {
                'created': created,
                'form': form,
            }
            return render(request, 'projects/project_form.html', context)
        else:
            return render(request, 'projects/project_form.html', context)
    else:
        form = ProjectRegistrationForm(use_required_attribute=False)
        context = {
            'form': form,
        }
        return render(request,'projects/project_form.html', context)

@user_passes_test(is_pm_or_admin)
def projects(request, company_id = None):
    order_by = request.GET.get('order_by')
    if order_by == None:
        order_by = 'id'
    direction = request.GET.get('direction')
    if direction == None:
        direction = 'desc'
    if direction == 'desc':
        ordering = '-{}'.format(order_by)
    else:
        ordering = order_by
    search_term = request.GET.get('search')
    if search_term is not None:
        if company_id is not None:
            projects = Project.objects.filter(
                (Q(name__icontains=search_term) | 
                                Q(description__icontains=search_term) | 
                                Q(company__name__icontains=search_term))
            ).filter(company_id=company_id).order_by(ordering)
        else:
            projects = Project.objects.filter(
                Q(name__icontains=search_term) | 
                Q(description__icontains=search_term) | 
                Q(company__name__icontains=search_term)
            ).order_by(ordering)
    else:
        if company_id is not None:
            projects = Project.objects.filter(company_id=company_id)
        else:
            projects = Project.objects.all()
    paginated_projects = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_projects.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/projects.html', context)

@user_passes_test(is_pm_or_admin)
def edit_project(request, project_id):
    project = Project.objects.get(id=project_id)
    form = ProjectRegistrationForm(instance=project, use_required_attribute=False)
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
    form = ProjectRegistrationForm(request.POST, instance=instance, use_required_attribute=False)
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
        changed_request = request.POST.copy()
        if request.POST.get('hours') == '':
            changed_request.update({'hours': 0})
        form = TaskRegistrationForm(changed_request, use_required_attribute=False)
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
        form = TaskRegistrationForm(use_required_attribute=False)
        context = {
            'form': form,
        }
        return render(request,'projects/task_form.html', context)

@user_passes_test(is_pm_or_admin)
def tasks(request, project_id = None):
    order_by = request.GET.get('order_by')
    if order_by == None:
        order_by = 'id'
    direction = request.GET.get('direction')
    if direction == None:
        direction = 'desc'
    if direction == 'desc':
        ordering = '-{}'.format(order_by)
    else:
        ordering = order_by
    search_term = request.GET.get('search')
    if search_term is not None:
        if project_id is not None:
            tasks = Task.objects.filter(
                Q(project__name__icontains=search_term) |
                Q(employee__username__icontains=search_term) |
                Q(task_name__icontains=search_term) |
                Q(status__icontains=search_term) |
                Q(deadline__icontains=search_term) |
                Q(start_date__icontains=search_term) |
                Q(hours__icontains=search_term) |
                Q(description__icontains=search_term)
            ).filter(project_id=project_id).order_by(ordering)
        else:
            tasks = Task.objects.filter(
                Q(project__name__icontains=search_term) |
                Q(employee__username__icontains=search_term) |
                Q(task_name__icontains=search_term) |
                Q(status__icontains=search_term) |
                Q(deadline__icontains=search_term) |
                Q(start_date__icontains=search_term) |
                Q(hours__icontains=search_term) |
                Q(description__icontains=search_term)
            ).order_by(ordering)
    else:
        if project_id is not None:
            tasks = Task.objects.filter(project_id=project_id)
        else:
            tasks = Task.objects.all()
    paginated_tasks = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_tasks.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/tasks.html', context)

@user_passes_test(is_pm_or_admin)
def edit_task(request, task_id):
    task = Task.objects.get(id=task_id)
    form = TaskRegistrationForm(instance=task, use_required_attribute=False)
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
    form = TaskRegistrationForm(request.POST, instance=instance, use_required_attribute=False)
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
        form = ChecklistRegistrationForm(request.POST, use_required_attribute=False)
        context = {'form': form}
        if form.is_valid():
            form.save()
            created = True
            form = ChecklistRegistrationForm(use_required_attribute=False)
            context = {
                'form': form,
                'created': created,
            }
            return render(request, 'projects/checklist_form.html', context)
        else:
            return render(request, 'projects/checklist_form.html', context)
    else:
        form = ChecklistRegistrationForm(use_required_attribute=False)
        context = {
            'form': form,
        }
        return render(request,'projects/checklist_form.html', context)

def checklists(request, task_id = None):
    order_by = request.GET.get('order_by')
    if order_by == None:
        order_by = 'id'
    direction = request.GET.get('direction')
    if direction == None:
        direction = 'desc'
    if direction == 'desc':
        ordering = '-{}'.format(order_by)
    else:
        ordering = order_by
    search_term = request.GET.get('search')
    if search_term is not None:
        if task_id is not None:
            checklists = Checklist.objects.filter(
                Q(checklist_name__icontains=search_term) |
                Q(task__task_name__icontains=search_term) |
                Q(status__icontains=search_term)
            ).filter(task_id=task_id).order_by(ordering)
        else:
            checklists = Checklist.objects.filter(
                Q(checklist_name__icontains=search_term) |
                Q(task__task_name__icontains=search_term) |
                Q(status__icontains=search_term)
            ).order_by(ordering)
    else:
        if task_id is not None:
            checklists = Checklist.objects.filter(task_id=task_id)
        else:
            checklists = Checklist.objects.all()
    paginated_checklists = Paginator(checklists, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_checklists.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/checklists.html', context)

def edit_checklist(request, checklist_id):
    checklist = Checklist.objects.get(id=checklist_id)
    form = ChecklistRegistrationForm(instance=checklist, use_required_attribute=False)
    context = {
        'id': checklist.id,
        'form': form,
        'edit': True
    }
    return render(request, 'projects/checklist_form.html', context)

def update_checklist(request):
    id = request.POST.get('id')
    instance = Checklist.objects.get(id = id)
    form = ChecklistRegistrationForm(request.POST, instance=instance, use_required_attribute=False)
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
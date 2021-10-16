from django.shortcuts import render
from django.db.models import Avg
from projects.models import Project, Task, Checklist
from projects.forms import ProjectRegistrationForm, TaskRegistrationForm, ChecklistRegistrationForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect
import csv
from django.http import HttpResponse
from core.views import is_admin, is_project_manager, is_pm_or_admin

# Create your views here.
@user_passes_test(is_pm_or_admin)
def new_project(request):
    if request.method == 'POST':
        form = ProjectRegistrationForm(request.POST, user=request.user, use_required_attribute=False)
        context = {'form': form}
        if form.is_valid():
            form.save()
            created = True
            form = ProjectRegistrationForm(user=request.user, use_required_attribute=False)
            context = {
                'created': created,
                'form': form,
            }
            return render(request, 'projects/project_form.html', context)
        else:
            print(form.errors)
            return render(request, 'projects/project_form.html', context)
    else:
        form = ProjectRegistrationForm(user=request.user, use_required_attribute=False)
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
    this_user = request.user
    if search_term is not None:
        if company_id is not None:
            projects = Project.objects.filter(admin=this_user.admin).filter(
                (Q(name__icontains=search_term) | 
                                Q(description__icontains=search_term) | 
                                Q(company__name__icontains=search_term))
            ).filter(company_id=company_id).order_by(ordering)
        else:
            projects = Project.objects.filter(admin=this_user.admin).filter(
                Q(name__icontains=search_term) | 
                Q(description__icontains=search_term) | 
                Q(company__name__icontains=search_term)
            ).order_by(ordering)
    else:
        if company_id is not None:
            projects = Project.objects.filter(company_id=company_id)
        else:
            projects = Project.objects.filter(admin=this_user.admin)
    paginated_projects = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_projects.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/projects.html', context)

@user_passes_test(is_pm_or_admin)
def edit_project(request, project_id):
    this_user = request.user
    project = Project.objects.filter(admin=this_user.admin).get(id=project_id)
    form = ProjectRegistrationForm(instance=project, user=request.user, use_required_attribute=False)
    context = {
        'id': project.id,
        'form': form,
        'edit': True
    }
    return render(request, 'projects/project_form.html', context)

@user_passes_test(is_pm_or_admin)
def update_project(request):
    this_user = request.user
    id = request.POST.get('id')
    instance = Project.objects.filter(admin=this_user.admin).get(id = id)
    form = ProjectRegistrationForm(request.POST, user=request.user, instance=instance, use_required_attribute=False)
    context = { 'form': form, 'id': instance.id, 'edit': True}
    if form.is_valid():
        form.save()
        context['updated'] = True
    return render(request, 'projects/project_form.html', context)

@user_passes_test(is_pm_or_admin)
def delete_project(request, project_id):
    this_user = request.user
    project = Project.objects.filter(admin=this_user.admin).get(id=project_id)
    project.delete()
    return redirect('projects:projects')

# Task CRUD - start
@user_passes_test(is_pm_or_admin)
def new_task(request):
    if request.method == 'POST':
        changed_request = request.POST.copy()
        if request.POST.get('hours') == '':
            changed_request.update({'hours': 0})
        if request.POST.get('estimate_hours') == '':
            changed_request.update({'estimate_hours': 0})
        form = TaskRegistrationForm(changed_request, user=request.user, use_required_attribute=False)
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
        form = TaskRegistrationForm(user=request.user,use_required_attribute=False)
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
    this_user = request.user
    if search_term is not None:
        if project_id is not None:
            tasks = Task.objects.filter(admin=this_user.admin).filter(
                Q(project__name__icontains=search_term) |
                Q(task_name__icontains=search_term) |
                Q(status__icontains=search_term) |
                Q(deadline__icontains=search_term) |
                Q(start_date__icontains=search_term) |
                Q(hours__icontains=search_term) |
                Q(description__icontains=search_term)
            ).filter(project_id=project_id).order_by(ordering)
        else:
            tasks = Task.objects.filter(admin=this_user.admin).filter(
                Q(project__name__icontains=search_term) |
                Q(task_name__icontains=search_term) |
                Q(status__icontains=search_term) |
                Q(deadline__icontains=search_term) |
                Q(start_date__icontains=search_term) |
                Q(hours__icontains=search_term) |
                Q(description__icontains=search_term)
            ).order_by(ordering)
    else:
        if project_id is not None:
            tasks = Task.objects.filter(admin=this_user.admin).filter(project_id=project_id)
        else:
            tasks = Task.objects.filter(admin=this_user.admin)
    paginated_tasks = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_tasks.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/tasks.html', context)

@user_passes_test(is_pm_or_admin)
def edit_task(request, task_id):
    this_user = request.user
    task = Task.objects.filter(admin=this_user.admin).get(id=task_id)
    form = TaskRegistrationForm(instance=task, user=request.user, use_required_attribute=False)
    context = {
        'id': task.id,
        'form': form,
        'edit': True
    }
    return render(request, 'projects/task_form.html', context)

@user_passes_test(is_pm_or_admin)
def update_task(request):
    this_user = request.user
    id = request.POST.get('id')
    instance = Task.objects.filter(admin=this_user.admin).get(id = id)
    form = TaskRegistrationForm(request.POST, instance=instance, user=request.user, use_required_attribute=False)
    context = { 'form': form, 'id': instance.id, 'edit': True}
    if form.is_valid():
        form.save()
        context['updated'] = True
    return render(request, 'projects/task_form.html', context)

@user_passes_test(is_pm_or_admin)
def delete_task(request, task_id):
    this_user = request.user
    task = Task.objects.filter(admin=this_user.admin).get(id=task_id)
    task.delete()
    return redirect('projects:tasks')
# Task CRUD - end

#Checklist CRUD - start
def new_checklist(request):
    if request.method == 'POST':
        form = ChecklistRegistrationForm(request.POST, user=request.user, use_required_attribute=False)
        context = {'form': form}
        if form.is_valid():
            form.save()
            created = True
            form = ChecklistRegistrationForm(user=request.user, use_required_attribute=False)
            context = {
                'form': form,
                'created': created,
            }
            return render(request, 'projects/checklist_form.html', context)
        else:
            return render(request, 'projects/checklist_form.html', context)
    else:
        form = ChecklistRegistrationForm(user=request.user, use_required_attribute=False)
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
    this_user = request.user
    if search_term is not None:
        if task_id is not None:
            checklists = Checklist.objects.filter(admin=this_user.admin).filter(
                Q(checklist_name__icontains=search_term) |
                Q(task__task_name__icontains=search_term) |
                Q(status__icontains=search_term)
            ).filter(task_id=task_id).order_by(ordering)
        else:
            checklists = Checklist.objects.filter(admin=this_user.admin).filter(
                Q(checklist_name__icontains=search_term) |
                Q(task__task_name__icontains=search_term) |
                Q(status__icontains=search_term)
            ).order_by(ordering)
    else:
        if task_id is not None:
            checklists = Checklist.objects.filter(admin=this_user.admin).filter(task_id=task_id)
        else:
            checklists = Checklist.objects.filter(admin=this_user.admin)
    paginated_checklists = Paginator(checklists, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_checklists.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/checklists.html', context)

def edit_checklist(request, checklist_id):
    this_user = request.user
    checklist = Checklist.objects.filter(admin=this_user.admin).get(id=checklist_id)
    form = ChecklistRegistrationForm(instance=checklist, user=request.user, use_required_attribute=False)
    context = {
        'id': checklist.id,
        'form': form,
        'edit': True
    }
    return render(request, 'projects/checklist_form.html', context)

def update_checklist(request):
    this_user = request.user
    id = request.POST.get('id')
    instance = Checklist.objects.filter(admin=this_user.admin).get(id = id)
    form = ChecklistRegistrationForm(request.POST, instance=instance, user=request.user, use_required_attribute=False)
    context = { 'form': form, 'id': instance.id, 'edit': True}
    if form.is_valid():
        form.save()
        context['updated'] = True
    return render(request, 'projects/checklist_form.html', context)

def delete_checklist(request, checklist_id):
    this_user = request.user
    checklist = Checklist.objects.filter(admin=this_user.admin).get(id=checklist_id)
    checklist.delete()
    return redirect('projects:checklists')
#Checklist CRUD - end

@user_passes_test(is_admin)
def export_tasks(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
    writer = csv.writer(response)
    writer.writerow(['Task', 'Description', 'Hours', 'Created Date', 'Status', 'POC'])

    tasks = Task.objects.all().values_list('task_name', 'description', 'hours', 'created_at', 'status', 'employee__first_name')
    total_hours = 0
    for task in tasks:
        total_hours += task[2]
        writer.writerow(task)
    writer.writerow(())
    writer.writerow(('', 'Total Hours', total_hours))
    return response

def last_worked_employee(project_id):
    Task.objects.get(project_id = project_id)
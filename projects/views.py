from django.shortcuts import render
from django.db.models import Avg
from projects.models import Project, Task, Checklist
from projects.forms import ProjectRegistrationForm, TaskRegistrationForm, ChecklistRegistrationForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect
import csv
import codecs
from django.http import HttpResponse
from core.views import is_admin, is_project_manager, is_pm_or_admin
from django.contrib.auth import get_user_model
User = get_user_model()
from .forms import status as form_status

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
# @user_passes_test(is_pm_or_admin)
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

# @user_passes_test(is_pm_or_admin)
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

# @user_passes_test(is_pm_or_admin)
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

# @user_passes_test(is_pm_or_admin)
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
            checklists = Checklist.objects.filter(admin=this_user.admin, task_id=task_id, user=this_user).filter(
                Q(checklist_name__icontains=search_term) |
                Q(task__task_name__icontains=search_term) |
                Q(status__icontains=search_term)
            ).order_by(ordering)
        else:
            checklists = Checklist.objects.filter(admin=this_user.admin, user=this_user).filter(
                Q(checklist_name__icontains=search_term) |
                Q(task__task_name__icontains=search_term) |
                Q(status__icontains=search_term)
            ).order_by(ordering)
    else:
        if task_id is not None:
            checklists = Checklist.objects.filter(admin=this_user.admin, task_id=task_id, user=this_user)
        else:
            checklists = Checklist.objects.filter(admin=this_user.admin, user=this_user)
    paginated_checklists = Paginator(checklists, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_checklists.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'projects/checklists.html', context)

def edit_checklist(request, checklist_id):
    this_user = request.user
    checklist = Checklist.objects.filter(admin=this_user.admin, user=this_user).get(id=checklist_id)
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
    instance = Checklist.objects.filter(admin=this_user.admin, user=this_user).get(id = id)
    form = ChecklistRegistrationForm(request.POST, instance=instance, user=request.user, use_required_attribute=False)
    context = { 'form': form, 'id': instance.id, 'edit': True}
    if form.is_valid():
        form.save()
        context['updated'] = True
    return render(request, 'projects/checklist_form.html', context)

def delete_checklist(request, checklist_id):
    this_user = request.user
    checklist = Checklist.objects.filter(admin=this_user.admin, user=this_user).get(id=checklist_id)
    checklist.delete()
    return redirect('projects:checklists')
#Checklist CRUD - end

@user_passes_test(is_admin)
def download_import_sample(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
    writer = csv.writer(response)
    writer.writerow(['Task', 'Description', 'Hours', 'Created Date', 'Status', 'Deadline', 'POC', 'Start Date', 'Estimate Hours'])
    writer.writerow(['Your Task Name', 'Your Description Here', 8, '2021/10/19 12:21:38', 'Yet to start', '2021/10/19 12:21:38', 'employee@email.com', '2021/10/19 12:21:38', 10])
    return response

@user_passes_test(is_admin)
def import_tasks(request):
    context = {}
    admin = request.user.admin
    projects = Project.objects.filter(admin=admin)
    context = {'projects': projects, 'errors': []}
    if request.method == 'POST':
        file = request.FILES['file']
        user = request.user
        project = Project.objects.filter(admin = admin).get()
        reader = csv.DictReader(codecs.iterdecode(file, 'utf-8'))
        for row in reader:
            task_name = row['Task']
            description = row['Description']
            hours = row['Hours']
            created_at = row['Created Date']
            status = list(filter(lambda x: x[1].lower() == row['Status'].lower(), form_status))
            status = status[0][0]
            deadline = row['Deadline']
            poc = row['POC']
            try:
                employee = User.objects.filter(admin=admin).get(email=row['POC'])
            except User.DoesNotExist:
                employee = None
                context['errors'].append(f'{poc} does not exist')
            start_date = row['Start Date']
            estimate_hours= row['Estimate Hours']
            created = user
            Task.objects.create(admin=admin, project=project, employee=employee, task_name=task_name, status=status, deadline=deadline, start_date=start_date, estimate_hours=estimate_hours, hours=hours, description=description, created=created, created_at=created_at, updated=created, updated_at=created_at, imported=True)
        file.close()
        context['created'] = True
    return render(request, 'projects/import-tasks.html', context)

@user_passes_test(is_admin)
def export_tasks(request):
    admin = request.user.admin
    projects = Project.objects.filter(admin=admin)
    fields = [f.name for f in Task._meta.get_fields()]
    fields.remove('deleted')
    fields.remove('created')
    fields.remove('updated')
    fields.remove('imported')
    fields.remove('admin')
    fields.remove('project')
    context = {'projects': projects, 'fields': fields, 'errors': []}
    if request.method == 'POST':
        request_fields = request.POST.getlist('fields')
        project = Project.objects.filter(admin=admin).get(id=request.POST.get('project'))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{project.name}.csv"'
        writer = csv.writer(response)
        need_checklist = False
        if 'checklist' in  request_fields:
            need_checklist = True
        request_fields.remove('checklist')
        writer.writerow([i.title().replace('_', ' ') for i in request_fields])
        request_columns = list(request_fields)
        if 'id' not in request_fields:
            request_columns.append('id')
        tasks = Task.objects.filter(admin=admin, project=project).values(*request_columns)
        total_hours = 0
        empty_row_data = ['' for i in request_fields]
        date_fields = ['start_date', 'deadline', 'created_at', 'updated_at']
        for task in tasks:
            value_row = []
            for request_field in request_fields:
                if request_field == 'hours':
                    total_hours += task[request_field]
                elif request_field == 'employee':
                    this_employee = User.objects.filter(admin=admin, id=task[request_field]).values_list('first_name', flat=True).first()
                    task[request_field] = this_employee
                elif request_field in date_fields:
                    task[request_field] = task[request_field].strftime(("%d-%m-%Y %H:%M:%S"))
                value_row.append(task[request_field])
            writer.writerow(value_row)
            if need_checklist:
                checklists = Checklist.objects.filter(admin=admin, task=task.get('id')).values()
                for checklist in checklists:
                    checklist_row = list(empty_row_data)
                    task_name_index = 0
                    if 'task_name' in  request_fields:
                        task_name_index = request_fields.index('task_name')
                    checklist_row[task_name_index] = checklist.get('checklist_name')
                    writer.writerow(checklist_row)
        if total_hours != 0:
            writer.writerow(())
            hours_index = request_fields.index('hours')
            total_hours_row = list(empty_row_data)
            if hours_index == 0:
                total_hours_row[0] = 'Total Hours'
                total_hours_row[1] = total_hours
            else:
                total_hours_row[hours_index - 1] = 'Total Hours'
                total_hours_row[hours_index] = total_hours
            writer.writerow(total_hours_row)
        return response
    return render(request, 'projects/export-tasks.html', context)

def last_worked_employee(project_id):
    Task.objects.get(project_id = project_id)
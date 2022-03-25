from projects.email import EmailThread
from django.conf import settings
from email import message
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .forms import StandupRegistrationForm
from projects.forms import TaskRegistrationForm
from projects.models import Task
from django.shortcuts import redirect
from django.urls import reverse
from django.core.mail import send_mail
from standup.models import Standup, Task as StandupTask
import datetime
from django.contrib.auth import get_user_model
User = get_user_model()
from register.models import Attendance

# Create your views here.
def index(request):
    return render(request, 'standups.html')

def employee_select(request):
    date = request.GET.get('date')
    if date is None:
        date = datetime.date.today().strftime('%Y-%m-%d')
    # else:
    #     date = datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    added_employee_ids = Standup.objects.filter(employee__admin=request.user.admin).filter(
        employee__groups__name__in=['employee', 'project_manager', 'admin']).filter(created_at__date=date).values_list('employee_id', flat=True)
    employees = User.objects.filter(admin=request.user.admin).filter(
        groups__name__in=['employee', 'project_manager', 'admin']).order_by('first_name')
    context = {'added_employee_ids': added_employee_ids, 'employees': employees, 'date': date}
    return render(request, 'employee_select.html', context)

def new_standup(request, employee_id = None):
    form = StandupRegistrationForm(
        user=request.user, use_required_attribute=False)
    standup = Standup.objects.filter(employee__admin=request.user.admin).filter(
        created_at__date=datetime.date.today()).filter(employee_id=employee_id)
    if request.method == 'POST':
        employee = request.POST.get('employee')
        tasks = request.POST.getlist('task[]')
        task_ids = request.POST.get('pending_task_ids[]')
        form = StandupRegistrationForm(
            request.POST, user=request.user, use_required_attribute=False)
        if task_ids:
            task_ids = task_ids.split(',')
        else:
            task_ids = []
        if not (len(tasks) or len(task_ids)):
            messages.error(request, 'Add or pull task(s)')
        else:
            if form.is_valid():
                saved_standup = None
                if standup.exists():
                    # messages.error(request, 'Daily standup is added already for this employee')
                    saved_standup = standup[0]
                task_request = request.POST.copy()
                if request.POST.get('hours') is None:
                    task_request.update({'hours': 0})
                if request.POST.get('estimate_hours') is None:
                    task_request.update({'estimate_hours': 0})
                if request.POST.get('status') is None:
                    task_request.update({'status': 1})
                if request.POST.get('start_date') is None:
                    now = datetime.datetime.now()
                    now.strftime("%Y-%m-%d %H:%M:%S")
                    task_request.update({'start_date': now})
                for task in tasks:
                    task_request.update({'task_name': task})
                    task_form = TaskRegistrationForm(
                        task_request, user=request.user, use_required_attribute=False)
                    if task_form.is_valid():
                        saved_task = task_form.save()
                        task_ids.append(saved_task.id)
                        # Email functionality start
                        if request.user.id != int(employee):
                            employee_email = User.objects.get(pk=employee)
                            url = f'{request.get_host()}/projects/edit-task/{saved_task.id}'
                            html_mail_content = (request.user.first_name if request.user.first_name is not None else '') + ' ' + (
                                request.user.last_name if request.user.last_name is not None else '') + ' has assinged you a task \n' + url
                            EmailThread('Task has been assigned', html_mail_content, [
                                        employee_email]).start()
                        # Email -End
                    else:
                        if task_request.get('project'):
                            messages.error(
                                request, 'Failed to create Task')
                        else:
                            messages.error(
                                request, 'Select a project')
                if len(task_ids):
                    if saved_standup is None:
                        saved_standup = form.save()
                    for task_id in task_ids:
                        StandupTask.objects.create(admin=request.user.admin, standup_id=saved_standup.id, task_id=task_id)
                
                    # Attendance functionality start
                    type = 2  # Work From Home
                    if True:
                        type = 1  # Office
                    today = datetime.date.today()
                    employee = User.objects.get(pk=employee)
                    if not Attendance.objects.filter(admin=request.user.admin, employee=employee, work_date__date=today).exists():
                        Attendance.objects.create(
                            admin=request.user.admin, employee=employee, type=type)
                    # Attendance functionality end
                    # messages.success(request, "Success")
                    created = True
                    context = {
                        'created': created,
                        'form': form,
                    }
                    messages.success(request, 'Task has been assigned.')
                    # return redirect(reverse('standup:new_standup', args=(int(employee),)))
                    return redirect(reverse('standup:employee_select'))
                else:
                    messages.error(request, 'No tasks have been created')
            else:
                messages.error(request, 'Failed to create standup')

    employee = User.objects.filter(
        admin=request.user.admin).filter(pk=employee_id)
    pending_tasks = Task.objects.filter(employee=employee_id, status__in=(
        1, 2)).values('id', 'task_name')
    context = {
        'form': form,
        'employee': employee,
        'pending_tasks': pending_tasks,
        'is_standup_exist': standup.exists()
    }
    return render(request, 'standup_form.html', context)

def view_standup(request, employee_id):
    date = request.GET.get('date')
    if date is None:
        date = datetime.date.today().strftime('%Y-%m-%d')
    # standups = Standup.objects.filter(employee__admin=request.user.admin).filter(
        # employee__groups__name__in=['employee', 'project_manager']).filter(employee_id=employee_id).filter(created_at__date=date)
    standup_tasks = StandupTask.objects.filter(admin=request.user.admin).filter(standup__employee_id=employee_id).filter(standup__created_at__date=date)
    print(standup_tasks.values())
    context = {
        'standup_tasks': standup_tasks
    }
    return render(request, 'view_standup.html', context)

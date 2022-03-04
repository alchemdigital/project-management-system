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

# Create your views here.
def index(request):
    return render(request, 'standups.html')

def employee_select(request):
    date = request.GET.get('date')
    if date is None:
        date = datetime.date.today()
    # else:
    #     date = datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    added_employee_ids = Standup.objects.filter(employee__admin=request.user.admin).filter(
        employee__groups__name__in=['employee', 'project_manager']).filter(created_at__date=date).values_list('employee_id', flat=True)
    employees = User.objects.filter(admin=request.user.admin).filter(
        groups__name__in=['employee', 'project_manager'])
    context = {'added_employee_ids': added_employee_ids, 'employees': employees}
    return render(request, 'employee_select.html', context)

def new_standup(request, employee_id = None):
    form = StandupRegistrationForm(
        user=request.user, use_required_attribute=True)
    if request.method == 'POST':
        employee = request.POST.get('employee')
        standup = Standup.objects.filter(employee__admin=request.user.admin).filter(created_at__date=datetime.date.today()).filter(employee_id=employee)
        if standup.exists():
            messages.error(request, 'Daily standup is added already for this employee')
        else:
            standup_request = request.POST.copy()
            tasks = request.POST.getlist('task[]')
            task_ids = request.POST.get('pending_task_ids[]').split(',')
            if not (len(tasks) or (len(task_ids) and task_ids[0] != '')):
                messages.error(
                    request, 'Add or pull task(s)')
            else:
                form = StandupRegistrationForm(
                    standup_request, user=request.user, use_required_attribute=False)
                if form.is_valid():
                    task_request = request.POST.copy()
                    if request.POST.get('hours') is None:
                        task_request.update({'hours': 0})
                    if request.POST.get('estimate_hours') is None:
                        task_request.update({'estimate_hours': 0})
                    if request.POST.get('status') is None:
                        task_request.update({'status': 1})
                    for task in tasks:
                        task_request.update({'task_name': task})
                        task_form = TaskRegistrationForm(
                            task_request, user=request.user, use_required_attribute=False)
                        if task_form.is_valid():
                            saved_task = task_form.save()
                            task_ids.append(saved_task.id)
                        else:
                            messages.error(request, 'Failed to create Task')
                    saved_standup = form.save()
                    if len(task_ids):
                        for task_id in task_ids:
                            StandupTask.objects.create(admin=request.user.admin, standup_id=saved_standup.id, task_id=task_id)
                    
                    # messages.success(request, "Success")
                    # Email functionality start
                    if request.user.id != int(employee):
                        employee_email = User.objects.get(pk=employee)
                        url = request.get_host()+'/projects/tasks'
                        html_mail_content = (request.user.first_name if request.user.first_name is not None else '') + ' ' + (
                            request.user.last_name if request.user.last_name is not None else '') + ' has assinged you a task \n' + url
                        EmailThread('Task Assigned', html_mail_content, [employee_email]).start()
                    # Email -End
                    created = True
                    context = {
                        'created': created,
                        'form': form,
                    }
                    # return redirect(reverse('standup:new_standup', args=(int(employee),)))
                    return redirect(reverse('standup:employee_select'))
                else:
                    messages.error(request, 'Failed to create standup')

    employee = User.objects.filter(
        admin=request.user.admin).filter(pk=employee_id)
    pending_tasks = Task.objects.filter(employee=employee_id, status__in=(
        1, 2)).values('id', 'task_name')
    context = {
        'form': form,
        'employee': employee,
        'pending_tasks': pending_tasks
    }
    return render(request, 'standup_form.html', context)

def view_standup(request, employee_id):
    standup = Standup.objects.filter(employee__admin=request.user.admin).filter(
        employee__groups__name__in=['employee', 'project_manager']).filter(created_at__date=datetime.date.today())
    context = {
        'standup': standup
    }
    return render(request, 'view_standup.html', context)

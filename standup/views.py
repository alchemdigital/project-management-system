from django.conf import settings
from email import message
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .forms import StandupRegistrationForm, StandupTaskRegistration
from projects.forms import TaskRegistrationForm
from projects.models import Task
from django.shortcuts import redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
def index(request):
    return render(request, 'standups.html')


def new_standup(request):
    if request.method == 'POST':
        form = StandupRegistrationForm(
            request.POST, user=request.user, use_required_attribute=False)
        if form.is_valid():
            standup = form.save()
            tasks = request.POST.getlist('task[]')
            changed_request = request.POST.copy()
            if request.POST.get('hours') is None:
                changed_request.update({'hours': 0})
            if request.POST.get('estimate_hours') is None:
                changed_request.update({'estimate_hours': 0})
            if request.POST.get('status') is None:
                changed_request.update({'status': 1})
            employee = request.POST.get('employee')
            for task in tasks:
                changed_request.update({'task_name': task})
                task_form = TaskRegistrationForm(
                    changed_request, user=request.user, use_required_attribute=False)
                if task_form.is_valid():
                    saved_task = task_form.save()
                    if request.POST.get('task_id') is None:
                        changed_request.update({'task': saved_task.id})
                    if request.POST.get('standup_id') is None:
                        changed_request.update({'standup': standup.id})
                    standup_task = StandupTaskRegistration(
                        changed_request, user=request.user, use_required_attribute=False)
                    if standup_task.is_valid():
                        standup_task.save()
                    else:
                        messages.error(request, 'Failed to create Task')
                else:
                    messages.error(request, 'Failed to create Task')
            messages.success(request, "Success")
            # Email functionality start
            if request.user.id != employee:
                employee_email = User.objects.get(pk=employee)
                url = request.get_host()+'/projects/tasks'
                message = request.user.first_name+" " +request.user.last_name+" has assinged you a task \n"+url
                send_mail('Task Assigned', message, '', [employee_email], fail_silently=True)
            # Email -End
            created = True
            context = {
                'created': created,
                'form': form,
            }
            return redirect(reverse('standup:new-standup'))
        else:
            messages.error(request, 'Failed to create standup')
            context = {
                'form': form
            }
            return render(request, 'standup_form.html', context)
    else:
        form = StandupRegistrationForm(
            user=request.user, use_required_attribute=False)
        context = {
            'form': form
        }
        return render(request, 'standup_form.html', context)

def standup(request):
    pass    

def pending(request):
    employee_id = request.GET.get('employee_id')
    pending_task = Task.objects.filter(employee=employee_id, status__in=(1, 2)).values('id', 'task_name')
    return JsonResponse({'employee_id': employee_id, 'task': list(pending_task)})




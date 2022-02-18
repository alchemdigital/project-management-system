from email import message
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .forms import StandupRegistrationForm, StandupTaskRegistration
from projects.forms import TaskRegistrationForm
from projects.models import Task
from django.shortcuts import redirect
from django.urls import reverse

# Create your views here.
def index(request):
    return render(request, 'standups.html')


def new_standup(request):
    if request.method == 'POST':
        form = StandupRegistrationForm(request.POST, user=request.user)
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
                        messages.success(request, "Success")
                    else:
                        messages.error(request, 'Error in creating Task')
                else:
                    messages.error(request, 'Error in creating Task')
            created = True
            context = {
                'created': created,
                'form': form,
            }
            return redirect(reverse('standup:new-standup'))
        else:
            messages.error(request, 'Error in creating Standup')
            context = {
                'form': form
            }
            return render(request, 'standup_form.html', context)
    else:
        form = StandupRegistrationForm(user=request.user)
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




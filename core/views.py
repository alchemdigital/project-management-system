import calendar
from datetime import datetime
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.urls import reverse
from django.http import HttpResponseRedirect
from register.models import Company
from register.models import Project
from projects.models import Task
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Create your views here.
def index(request):
    return render(request, 'core/index.html')

def is_project_manager(user):
    return user.groups.filter(name='project_manager').exists()

def is_admin(user):
    return user.groups.filter(name='admin').exists()

def is_pm_or_admin(user):
    return user.groups.filter(Q(name='project_manager') | Q(name='admin')).exists()

def is_logged_in(user):
    return user.is_authenticated

@login_required
def dashboard(request):
    users = User.objects.all()
    active_users = User.objects.all().filter(is_active=True)
    companies = Company.objects.all()
    projects = Project.objects.all()
    tasks = Task.objects.all()
    date = datetime.today()
    start_date = calendar.monthrange(date.year, date.month)[0]
    end_date = calendar.monthrange(date.year, date.month)[1]
    start_date = date.replace(day=start_date).strftime('%Y-%m-%d')
    end_date = date.replace(day=end_date).strftime('%Y-%m-%d')
    context = {
        'users' : users,
        'active_users' : active_users,
        'companies' : companies,
        'projects' : projects,
        'tasks' : tasks,
        'start_date' : start_date,
        'end_date' : end_date
    }
    return render(request, 'core/dashboard.html', context)



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            authenticated_user = authenticate(username=request.POST['username'], password=request.POST['password'])
            login(request, authenticated_user)
            return redirect('core:dashboard')
        else:
            return render(request, 'register/login.html', {'login_form':form})
    else:
        form = AuthenticationForm()
    return render(request, 'register/login.html', {'login_form':form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('core:index'))

def context(request): # send context to base.html
    # if not request.session.session_key:
    #     request.session.create()
    users = User.objects.all()
    if request.user.is_authenticated:
        try:
            user_id = request.user.userprofile_set.values_list()[0][0]
            logged_user = UserProfile.objects.get(id=user_id)
            friends = logged_user.friends.all()
            context = {
                'users': users,
                'users_prof': users_prof,
                'logged_user': logged_user,
                'friends' : friends,
            }
            return context
        except:
            context = {
                'users':users,
            }
            return context
    else:
        context = {
            'users': users,
        }
        return context

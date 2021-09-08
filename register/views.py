from django.shortcuts import render
from django.contrib.auth import login
from django.shortcuts import redirect
from projects.models import Task
from .models import UserProfile
from .forms import RegistrationForm
from .forms import CompanyRegistrationForm
from .forms import ProfilePictureForm
from django.contrib.auth.models import Group
from projects.email import EmailThread
from django.contrib.auth.models import User

# Create your views here.
def register(request):
    if request.method == 'POST':
        changedRequest = request.POST.copy()
        generated_password = User.objects.make_random_password()
        print(generated_password)
        changedRequest.update({'password1': [generated_password]})
        form = RegistrationForm(changedRequest)
        roles = Group.objects.all().order_by('id')
        context = {
            'form':form,
            'roles' : roles
        }
        role = request.POST.get('role')
        if form.is_valid():
            user = form.save()
            thisRole = Group.objects.get(id = role)
            thisRole.user_set.add(user)
            # Email send functionality starts
            html_mail_content = f'<table border="1"><thead><th>username</th><th>Email</th><th>Password</th><tbody><td>{user.username}</td><td>{user.email}</td><td>{ generated_password }</td></tbody></table>'
            recipient_list = [user.email]
            EmailThread('Registered With PMS', html_mail_content, recipient_list).start()
            # Email send functionality ends
            created = True
            # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            context = {
                'form':form,
                'roles' : roles, 
                'created' : created
            }
            return render(request, 'register/reg_form.html', context)
        else:
            return render(request, 'register/reg_form.html', context)
    else:
        form = RegistrationForm()
        roles = Group.objects.all().order_by('id')
        context = {
            'form' : form,
            'roles' : roles
        }
        return render(request, 'register/reg_form.html', context)


def usersView(request):
    users = UserProfile.objects.all()
    tasks = Task.objects.all()
    context = {
        'users': users,
        'tasks': tasks,
    }
    return render(request, 'register/users.html', context)

def user_view(request, profile_id):
    user = UserProfile.objects.get(id=profile_id)
    context = {
        'user_view' : user,
    }
    return render(request, 'register/user.html', context)


def profile(request):
    if request.method == 'POST':
        img_form = ProfilePictureForm(request.POST, request.FILES)
        print('PRINT 1: ', img_form)
        context = {'img_form' : img_form }
        if img_form.is_valid():
            img_form.save(request)
            updated = True
            context = {'img_form' : img_form, 'updated' : updated }
            return render(request, 'register/profile.html', context)
        else:
            return render(request, 'register/profile.html', context)
    else:
        img_form = ProfilePictureForm()
        context = {'img_form' : img_form }
        return render(request, 'register/profile.html', context)


def newCompany(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        context = {'form':form}
        if form.is_valid():
            form.save()
            created = True
            form = CompanyRegistrationForm()
            context = {
                'created' : created,
                'form' : form,
                       }
            return render(request, 'register/new_company.html', context)
        else:
            return render(request, 'register/new_company.html', context)
    else:
        form = CompanyRegistrationForm()
        context = {
            'form' : form,
        }
        return render(request, 'register/new_company.html', context)

def get_active_profile(request):
    user_id = request.user.userprofile_set.values_list()[0][0]
    return UserProfile.objects.get(id=user_id)

def friends(request):
    if request.user.is_authenticated:
        user = get_active_profile(request)
        friends = user.friends.all()
        context = {
            'friends' : friends,
        }
    else:
        users_prof = UserProfile.objects.all()
        context= {
            'users_prof' : users_prof,
        }
    return render(request, 'register/friends.html', context)
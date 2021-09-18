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
from django.contrib.auth.forms import PasswordResetForm
from django.db.models import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.decorators import user_passes_test

def is_project_manager(user):
    return user.groups.filter(name='project_manager').exists()

def is_admin(user):
    return user.groups.filter(name='admin').exists()

def is_pm_or_admin(user):
    return user.groups.filter(Q(name='project_manager') | Q(name='admin')).exists()

# Create your views here.
@user_passes_test(is_admin)
def register(request):
    if request.method == 'POST':
        changed_request = request.POST.copy()
        generated_password = User.objects.make_random_password()
        changed_request.update({'password1': [generated_password]})
        form = RegistrationForm(changed_request)
        roles = Group.objects.all().order_by('id')
        role = request.POST.get('role')
        errors = {}
        if role == None:
            errors = {'role': ('Role is required',)}
        context = {
            'form': form,
            'roles': roles,
            'errors': errors
        }
        if role == None:
            return render(request, 'register/reg_form.html', context)
        if form.is_valid():
            user = form.save(commit = False)
            user.set_password(generated_password)
            user.save()
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

@user_passes_test(is_pm_or_admin)
def usersView(request):
    users = UserProfile.objects.all()
    tasks = Task.objects.all()
    context = {
        'users': users,
        'tasks': tasks,
    }
    return render(request, 'register/users.html', context)

@user_passes_test(is_pm_or_admin)
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

@user_passes_test(is_admin)
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

@user_passes_test(is_pm_or_admin)
def get_active_profile(request):
    user_id = request.user.userprofile_set.values_list()[0][0]
    return UserProfile.objects.get(id=user_id)

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "register/password_reset_email.txt"
                    context = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, context)
                    try:
                        send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("password-reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="register/password_reset.html", context={"password_reset_form":password_reset_form})
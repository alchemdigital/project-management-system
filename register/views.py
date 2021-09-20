from django.shortcuts import render
from django.contrib.auth import login
from django.shortcuts import redirect
from projects.models import Task
from .forms import RegistrationForm
from .forms import CompanyRegistrationForm
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
from .models import Company
from  django.core.paginator import Paginator

def is_project_manager(user):
    return user.groups.filter(name='project_manager').exists()

def is_admin(user):
    return user.groups.filter(name='admin').exists()

def is_pm_or_admin(user):
    return user.groups.filter(Q(name='project_manager') | Q(name='admin')).exists()

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

@user_passes_test(is_admin)
def users(request):
    users = User.objects.all().order_by('-id')
    paginated_users = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_users.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'register/users.html', context)

@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)
    form = RegistrationForm(instance=user)
    roles = Group.objects.all().order_by('id')
    selected_role = Group.objects.filter(user = user)
    context = {
        'id': user.id,
        'form': form,
        'roles' : roles,
        'selected_role': selected_role[0].id,
        'edit': True 
    }
    return render(request, 'register/reg_form.html', context)

@user_passes_test(is_admin)
def update_user(request):
    id = request.POST.get('id')
    role = request.POST.get('role')
    instance = User.objects.get(id = id)
    changed_request = request.POST.copy()
    # changed_request.update({'password1': 'asas'}) # This will not be updated
    form = RegistrationForm(changed_request, instance=instance)
    roles = Group.objects.all().order_by('id')
    selected_role = Group.objects.filter(user = instance)
    context = { 'form': form, 'id': instance.id, 'roles' : roles,
        'selected_role': selected_role[0].id, 'edit': True}
    if form.is_valid():
        form.save()
        thisRole = Group.objects.get(id = role)
        thisRole.user_set.add(instance)
        context['updated'] = True
    return render(request, 'register/reg_form.html', context)

@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = User.objects.get(id = user_id)
    user.delete()
    return redirect('register:users')

#Company CRUD - start
@user_passes_test(is_admin)
def new_company(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        context = { 'form': form }
        if form.is_valid():
            form.save()
            created = True
            form = CompanyRegistrationForm()
            context = {
                'created' : created,
                'form' : form,
            }
        
        return render(request, 'register/company_form.html', context)
    else:
        form = CompanyRegistrationForm()
        context = {
            'form' : form,
        }
        return render(request, 'register/company_form.html', context)

@user_passes_test(is_admin)
def companies(request):
    companies = Company.objects.all().order_by('-id')
    paginated_companies = Paginator(companies, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_companies.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'register/companies.html', context)

@user_passes_test(is_admin)
def edit_company(request, company_id):
    company = Company.objects.get(id=company_id)
    form = CompanyRegistrationForm(instance=company)
    context = {
        'id': company.id,
        'form': form,
        'edit': True
    }
    return render(request, 'register/company_form.html', context)

@user_passes_test(is_admin)
def update_company(request):
    id = request.POST.get('id')
    instance = Company.objects.get(id = id)
    form = CompanyRegistrationForm(request.POST, instance=instance)
    context = { 'form': form, 'id': instance.id, 'edit': True}
    if form.is_valid():
        form.save(id = instance.id)
        context['updated'] = True
    return render(request, 'register/company_form.html', context)

@user_passes_test(is_admin)
def delete_company(request, company_id):
    company = Company.objects.get(id = company_id)
    company.delete()
    return redirect('register:companies')
#Company CRUD - end

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
                        'domain': request.get_host(),
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': request.scheme,
                    }
                    email = render_to_string(email_template_name, context)
                    try:
                        send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("password-reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="register/password_reset.html", context={"password_reset_form":password_reset_form})
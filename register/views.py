from django.shortcuts import render
from django.contrib.auth import login
from django.shortcuts import redirect
from projects.models import Task
from .forms import RegistrationForm
from .forms import CompanyRegistrationForm
from django.contrib.auth.models import Group
from projects.email import EmailThread
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.forms import PasswordResetForm
from django.db.models import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Company, Attendance
from  django.core.paginator import Paginator
from core.views import is_admin, is_project_manager, is_pm_or_admin
from dal import autocomplete
import datetime

def admin_register(request):
    if request.method == 'POST':
        password = request.POST.get('password1')
        # User.objects.create(email=email, first_name=first_name, last_name=last_name, password=password)
        changed_request = request.POST.copy()
        form = RegistrationForm(changed_request)
        created = False
        if form.is_valid():
            user = form.save(commit = False)
            user.save()
            user.admin = user
            user.save()
            try:
                thisRole = Group.objects.get(id = 1)
                thisRole.user_set.add(user)
            except Group.DoesNotExist:
                pass
            # Email send functionality starts
            html_mail_content = f'<div>Your account has been created successfully</div>'
            recipient_list = [user.email]
            EmailThread('Registered With PMS', html_mail_content, recipient_list).start()
            # Email send functionality ends
            created = True
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        context = {
            'created' : created,
        }
        return redirect('/dashboard')
    else:
        form = RegistrationForm({})
        context = {
            'form': form
        }
        return render(request, 'register/admin_register.html', context)

@user_passes_test(is_admin)
def register(request):
    if request.method == 'POST':
        admin_id = request.user.id
        changed_request = request.POST.copy()
        generated_password = User.objects.make_random_password()
        changed_request.update({'password1': [generated_password]})
        changed_request.update({'admin_id': admin_id})
        form = RegistrationForm(changed_request)
        roles = Group.objects.all().exclude(name='admin').order_by('id')
        selected_roles = request.POST.getlist('role')
        errors = {}
        if selected_roles == None or not len(selected_roles):
            errors = {'role': ('Role is required',)}
        context = {
            'form': form,
            'roles': roles,
            'errors': errors
        }
        if selected_roles == None or not len(selected_roles):
            return render(request, 'register/reg_form.html', context)
        if form.is_valid():
            user = form.save(commit = False)
            user.set_password(generated_password)
            user.save()
            this_roles = Group.objects.filter(id__in = selected_roles)
            for this_role in this_roles:
                this_role.user_set.add(user)
            # Email send functionality starts
            html_mail_content = f'<table border="1"><thead><th>Email</th><th>Password</th><tbody><td>{user.email}</td><td>{ generated_password }</td></tbody></table>'
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
        admin_id = request.user.admin_id
        changed_request = ({'admin_id': admin_id})
        form = RegistrationForm(changed_request)
        roles = Group.objects.all().exclude(name='admin').order_by('id')
        selected_role = request.GET.get('role', None)
        context = {
            'form' : form,
            'roles' : roles,
        }
        if selected_role is not None:
            context['selected_role'] = int(selected_role)
        return render(request, 'register/reg_form.html', context)

@user_passes_test(is_admin)
def users(request):
    users = User.objects.filter(admin=request.user.admin).order_by('-id')
    paginated_users = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_users.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'register/users.html', context)

@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = request.user
    this_user = User.objects.get(id=user_id, admin=request.user.admin)
    form = RegistrationForm(instance=this_user)
    roles = Group.objects.all().exclude(name='admin').order_by('id')
    selected_roles = Group.objects.filter(user = this_user).values_list('id', flat=True)
    context = {
        'id': this_user.id,
        'form': form,
        'roles' : roles,
        'selected_roles': selected_roles,
        'edit': True 
    }
    return render(request, 'register/reg_form.html', context)

@user_passes_test(is_admin)
def update_user(request):
    id = request.POST.get('id')
    selected_roles = request.POST.getlist('role')
    instance = User.objects.get(id = id, admin=request.user.admin)
    changed_request = request.POST.copy()
    changed_request.update({'password1': ['this_will_not_be_updated']}) # This will not be updated. Only for validation
    form = RegistrationForm(changed_request, instance=instance)
    roles = Group.objects.all().exclude(name='admin').order_by('id')
    # selected_roles = Group.objects.filter(user = instance)
    context = { 'form': form, 'id': instance.id, 'roles' : roles,
        'selected_roles': selected_roles, 'edit': True}
    if form.is_valid():
        form.update(id = instance.id)
        this_roles = Group.objects.filter(id__in = selected_roles)
        for each_role in roles:
            each_role.user_set.remove(instance)
        for this_role in this_roles:
            this_role.user_set.add(instance)
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
        form = CompanyRegistrationForm(request.POST, user=request.user, use_required_attribute=False)
        context = { 'form': form }
        if form.is_valid():
            form.save()
            created = True
            form = CompanyRegistrationForm(user=request.user, use_required_attribute=False)
            context = {
                'created' : created,
                'form' : form,
            }
        
        return render(request, 'register/company_form.html', context)
    else:
        form = CompanyRegistrationForm(user=request.user, use_required_attribute=False)
        context = {
            'form' : form,
        }
        return render(request, 'register/company_form.html', context)

@user_passes_test(is_admin)
def companies(request):
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
        companies = Company.objects.filter(admin=this_user.admin).filter(
            Q(social_name__icontains=search_term) | 
            Q(name__icontains=search_term) | 
            Q(city__icontains=search_term) | 
            Q(found_date__icontains=search_term)
        ).order_by(ordering)
    else:
        companies = Company.objects.filter(admin=this_user.admin).order_by(ordering)
    paginated_companies = Paginator(companies, 10)
    page_number = request.GET.get('page')
    page_obj = paginated_companies.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'register/companies.html', context)

@user_passes_test(is_admin)
def edit_company(request, company_id):
    this_user = request.user
    company = Company.objects.get(id=company_id, admin=this_user.admin)
    form = CompanyRegistrationForm(user=request.user, instance=company, use_required_attribute=False)
    context = {
        'id': company.id,
        'form': form,
        'edit': True
    }
    return render(request, 'register/company_form.html', context)

@user_passes_test(is_admin)
def update_company(request):
    id = request.POST.get('id')
    this_user = request.user
    instance = Company.objects.get(id = id, admin=this_user.admin)
    form = CompanyRegistrationForm(request.POST, user=request.user, instance=instance, use_required_attribute=False)
    context = { 'form': form, 'id': instance.id, 'edit': True}
    if form.is_valid():
        form.save(id = instance.id)
        context['updated'] = True
    return render(request, 'register/company_form.html', context)

@user_passes_test(is_admin)
def delete_company(request, company_id):
    this_user = request.user
    company = Company.objects.get(id = company_id, admin=this_user.admin)
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
                    email_template_name = "register/password_reset_email.html"
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
                        send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False, html_message=email)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("password-reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="register/password_reset.html", context={"password_reset_form":password_reset_form})

@login_required
def attendance(request):
    user = request.user
    admin = request.user.admin
    today = datetime.date.today()
    today_present = Attendance.objects.filter(admin=user.admin, employee=user, work_date__date=today).exists()
    this_month_attendance = Attendance.objects.filter(admin=user.admin).extra(select={'datestr':"DATE_FORMAT(work_date, '%%Y-%%m-%%d')"})
    all_users = User.objects.filter(admin=admin)
    context = {
        'today_present': today_present,
        'this_month_attendance': this_month_attendance,
        'all_users': all_users,
    }
    return render(request, 'register/attendance.html', context)

@login_required
def add_attendance(request):
    user = request.user
    type = 2 # Work From Home
    if True:
        type = 1 # Office
    today = datetime.date.today()
    if not Attendance.objects.filter(admin=user.admin, employee=user, work_date__date=today).exists():
            Attendance.objects.create(admin=user.admin, employee=user, type=type)
    return redirect('/register/attendance')

class ClientAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        this_user = self.request.user
        if not is_admin(this_user):
            return User.objects.none()
        qs = User.objects
        if self.q:
            qs = qs.filter(admin=this_user.admin, groups=4).filter(Q(email__icontains=self.q) | Q(first_name__icontains=self.q))
        else:
            qs.none()
        return qs
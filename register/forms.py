from django import forms
from register.models import Company
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.forms import UserCreationForm
from dal import autocomplete

forms.DateInput.input_type="date"

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label='E-mail', required=True)
    password2 = None

    class Meta:
        model = User
        fields = {
            'first_name',
            'last_name',
            'email',
        }

        labels = {
            'first_name': 'Name',
            'last_name': 'Last Name',
        }

    def clean_data(self, field):
        if field == 'first_name':
            return self.cleaned_data['first_name']
        elif field == 'last_name':
            return self.cleaned_data['last_name']
        elif field == 'email':
            return self.cleaned_data['email']
        elif field == 'password1':
            return self.cleaned_data['password']
        elif field == 'admin_id':
            return self.cleaned_data['admin_id']

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.clean_data('first_name')
        user.last_name = self.clean_data('last_name')
        user.email = self.clean_data('email')
        if self.admin_id is not None:
            user.admin = User.objects.get(id=self.admin_id)
        if commit:
            user.save()
        return user

    def update(self, id):
        user = User.objects.get(id=id)
        user.first_name = self.clean_data('first_name')
        user.last_name = self.clean_data('last_name')
        user.email = self.clean_data('email')
        user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'E-mail'
        if kwargs.get('instance') is not None:
            self.admin_id = kwargs.get('instance').admin_id
        elif args and args[0] or False:
            self.admin_id = args[0]['admin_id']
        else:
            self.admin_id = None

class CompanyRegistrationForm(forms.ModelForm):
    # client = forms.ModelChoiceField(queryset=User.objects.none(), widget=autocomplete.ModelSelect2(url='register/client-autocomplete'), empty_label="Select a client *")

    class Meta:
        model = Company
        fields = ['social_name', 'name', 'client', 'city', 'found_date']

    def save(self, commit=True, id = None):
        if id is not None:
            company = Company.objects.get(id=id)
            company.updated = self.user
        else:
            company = Company()
            company.created = self.user
            company.updated = self.user
            company.admin = self.user.admin
        company.social_name = self.cleaned_data['social_name']
        company.name = self.cleaned_data['name']
        company.client = self.cleaned_data['client']
        company.city = self.cleaned_data['city']
        company.found_date = self.cleaned_data['found_date']
        if commit:
            company.save()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user')
        super(CompanyRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['social_name'] = forms.CharField(max_length=80)
        self.fields['social_name'].widget.attrs['class'] = 'form-control'
        self.fields['social_name'].widget.attrs['placeholder'] = 'Social Name *'
        self.fields['name'] = forms.CharField(max_length=80)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Name *'
        self.fields['client'] = forms.ModelChoiceField(queryset=User.objects.filter(admin=self.user.admin), widget=autocomplete.ModelSelect2(url='/register/client-autocomplete'), empty_label="Select a client *")
        self.fields['client'].widget.attrs['class'] = 'form-control'
        self.fields['city'] = forms.CharField(max_length=50)
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['placeholder'] = 'City *'
        self.fields['found_date'] = forms.DateField(required=False)
        self.fields['found_date'].widget.attrs['class'] = 'form-control'
        self.fields['found_date'].widget.attrs['type'] = 'date'
        self.fields['found_date'].widget.attrs['placeholder'] = 'Found date'
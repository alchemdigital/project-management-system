from django import forms
from register.models import Company as Comp
from register.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label='E-mail', required=True)
    password2 = None

    class Meta:
        model = User
        fields = {
            'username',
            'first_name',
            'last_name',
            'email',
        }

        labels = {
            'first_name': 'Name',
            'last_name': 'Last Name',
        }

    def clean_data(self, field):
        if field == 'username':
            return self.cleaned_data['username']
        elif field == 'first_name':
            return self.cleaned_data['first_name']
        elif field == 'last_name':
            return self.cleaned_data['last_name']
        elif field == 'email':
            return self.cleaned_data['email']
        elif field == 'password1':
            return self.cleaned_data['password']

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.username = self.clean_data('username')
        user.first_name = self.clean_data('first_name')
        user.last_name = self.clean_data('last_name')
        user.email = self.clean_data('email')
        if commit:
            user.save()
            user_profile = UserProfile.objects.create(user=user)
            user_profile.save()

        return user

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'E-mail'

class CompanyRegistrationForm(forms.Form):
    social_name = forms.CharField(max_length=80)
    name = forms.CharField(max_length=80)
    client = forms.ModelChoiceField(queryset=User.objects.filter(groups=4))
    city = forms.CharField(max_length=50)
    found_date = forms.DateField()

    class Meta:
        model = Comp


    def save(self, commit=True):
        company = Comp()
        company.social_name = self.cleaned_data['social_name']
        company.name = self.cleaned_data['name']
        company.client = self.cleaned_data['client']
        company.city = self.cleaned_data['city']
        company.found_date = self.cleaned_data['found_date']

        if commit:
            company.save()


    def __init__(self, *args, **kwargs):
        super(CompanyRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['social_name'].widget.attrs['class'] = 'form-control'
        self.fields['social_name'].widget.attrs['placeholder'] = 'Social Name'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Name'
        self.fields['client'].widget.attrs['class'] = 'form-control'
        self.fields['client'].widget.attrs['placeholder'] = 'Client'
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['placeholder'] = 'City'
        self.fields['found_date'].widget.attrs['class'] = 'form-control'
        self.fields['found_date'].widget.attrs['placeholder'] = 'Found date'


class ProfilePictureForm(forms.Form):
    img = forms.ImageField()
    class Meta:
        model = UserProfile
        fields = ['img']

    def save(self, request, commit=True):
        user = request.user.userprofile_set.first()
        user.img = self.cleaned_data['img']

        if commit:
            user.save()

        return user

    def __init__(self, *args, **kwargs):
        super(ProfilePictureForm, self).__init__(*args, **kwargs)
        self.fields['img'].widget.attrs['class'] = 'custom-file-input'
        self.fields['img'].widget.attrs['id'] = 'validatedCustomFile'
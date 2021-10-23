from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from projects.models import Project
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE, SOFT_DELETE_CASCADE

type = (
    ('1', 'Office'),
    ('2', 'Work From Home'),
)

class Company(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE # SOFT_DELETE -> Only delete current record, SOFT_DELETE_CASCADE -> Also delete relationships

    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    social_name = models.CharField(max_length=80)
    name = models.CharField(max_length=80)
    city = models.CharField(max_length=50)
    found_date = models.DateField(null=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_client', null=True, blank=True)
    created = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_created', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True, null = True)
    updated = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_updated', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now = True, null = True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ('name',)


    def __str__(self):
        return (self.name)

class Attendance(SafeDeleteModel):
    _safedelete_ploicy = SOFT_DELETE_CASCADE

    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_employee', null=True, blank=True)
    type = models.CharField(max_length=20, choices=type, default=1)
    work_date = models.DateTimeField(auto_now_add=True, null=True)
    created = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_created', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True, null = True)
    updated = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_updated', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now = True, null = True)

    class Meta:
        verbose_name_plural = 'Attendances'
        ordering = ('work_date',)

    def __str__(self):
        return (self.employee)

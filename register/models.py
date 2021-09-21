from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE, SOFT_DELETE_CASCADE

class Company(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE # SOFT_DELETE -> Only delete current record, SOFT_DELETE_CASCADE -> Also delete relationships

    social_name = models.CharField(max_length=80)
    name = models.CharField(max_length=80)
    city = models.CharField(max_length=50)
    found_date = models.DateField(null=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add = True, null = True)
    updated_at = models.DateTimeField(auto_now = True, null = True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ('name',)


    def __str__(self):
        return (self.name)

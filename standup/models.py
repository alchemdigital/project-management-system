from pyexpat import model
from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE, SOFT_DELETE_CASCADE
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Standup(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_employee', null=True)
    is_any_issue = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add = True, null = True)
    updated_at = models.DateTimeField(auto_now = True, null = True)


class Task(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    standup = models.ForeignKey('standup.Standup', on_delete=models.CASCADE)
    task = models.ForeignKey('projects.Task', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

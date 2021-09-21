from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE, SOFT_DELETE_CASCADE

status = (
    ('1', 'Yet to Start'),
    ('2', 'In Progress'),
    ('3', 'QC Pending'),
    ('4', 'Completed'),
)

# Create your models here.
class Project(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    name = models.CharField(max_length=80)
    slug = models.SlugField('shortcut', blank=True)
    company = models.ForeignKey('register.Company', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add = True, null = True)
    updated_at = models.DateTimeField(auto_now = True, null = True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return (self.name)

class Task(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # assigned_by = models.ManyToManyField(User)
    task_name = models.CharField(max_length=80)
    status = models.CharField(max_length=7, choices=status, default=1)
    deadline = models.DateField(null = True)
    start_date = models.DateField(null = True)
    hours = models.IntegerField(max_length = 5, null=True, default=0)
    description = models.TextField(null = True)
    created_at = models.DateTimeField(auto_now_add = True, null = True)
    updated_at = models.DateTimeField(auto_now = True, null = True)

    class Meta:
        ordering = ['project', 'task_name']

    def __str__(self):
        return(self.task_name)

class Checklist(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    checklist_name = models.CharField(max_length=255)
    status = models.CharField(max_length=7, choices=status, default=1)
    created_at = models.DateTimeField(auto_now_add = True, null = True)
    updated_at = models.DateTimeField(auto_now = True, null = True)

    class Meta:
        ordering = ['task', 'checklist_name']

    def __str__(self):
        return(self.checklist_name)
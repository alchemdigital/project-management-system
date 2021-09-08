from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE

status = (
    ('1', 'Stuck'),
    ('2', 'Working'),
    ('3', 'Done'),
)

# Create your models here.
class Project(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

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
    _safedelete_policy = SOFT_DELETE

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assign = models.ManyToManyField(User)
    # assigned_by = models.ManyToManyField(User)
    task_name = models.CharField(max_length=80)
    status = models.IntegerField(choices=status, default=1)
    deadline = models.DateField(null = True)
    start_date = models.DateField(null = True)
    hours = models.IntegerField(max_length = 5, default = 0)
    description = models.TextField(null = True)
    created_at = models.DateTimeField(auto_now_add = True, null = True)
    updated_at = models.DateTimeField(auto_now = True, null = True)

    class Meta:
        ordering = ['project', 'task_name']

    def __str__(self):
        return(self.task_name)

class Checklist(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    checklist_name = models.CharField(max_length=255)
    status = models.IntegerField(choices=status, default=1)
    created_at = models.DateTimeField(auto_now_add = True, null = True)
    updated_at = models.DateTimeField(auto_now = True, null = True)

    class Meta:
        ordering = ['task', 'checklist_name']

    def __str__(self):
        return(self.checklist_name)
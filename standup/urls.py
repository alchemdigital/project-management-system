from django.urls import path
from . import views

app_name = 'standup'

urlpatterns = [
    path('', views.index, name="standup"),
    path('new-standup', views.new_standup, name="new-standup"),
    path('standup', views.standup, name="standup"),
    path('get-pending', views.pending, name='pending-task')
]
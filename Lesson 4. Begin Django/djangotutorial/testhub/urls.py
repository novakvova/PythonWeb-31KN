from django.urls import path

from testhub import views

app_name = 'testhub'

urlpatterns = [
    path('', views.test_list, name='list'),
]

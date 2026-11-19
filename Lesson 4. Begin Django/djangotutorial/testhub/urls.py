from django.urls import path

from testhub import views

app_name = 'testhub'

urlpatterns = [
    path('', views.test_list, name='list'),
    path('<int:test_id>/', views.test_start, name='start'),
]
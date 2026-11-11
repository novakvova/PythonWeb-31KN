from django.urls import path

from testhub import views

app_name = 'testhub'

urlpatterns = [
    path('', views.test_list, name='list'),
    path('<int:test_id>/', views.test_start, name='start'),
    path('<int:test_id>/take/', views.test_take, name='take'),
    path('result/<int:result_id>/', views.test_result, name='result'),
]

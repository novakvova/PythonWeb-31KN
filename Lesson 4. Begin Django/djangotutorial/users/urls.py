from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name="logout"),

    path('password_reset/', views.password_reset_request, name="password_reset"),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
]
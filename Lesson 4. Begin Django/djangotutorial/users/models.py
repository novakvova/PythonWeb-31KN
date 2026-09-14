from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# Таблиці в БД
class CustomUser(AbstractUser):
    image_small = models.CharField(max_length=255, null=True, blank=True)
    image_medium = models.CharField(max_length=255, null=True, blank=True)
    image_large = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email

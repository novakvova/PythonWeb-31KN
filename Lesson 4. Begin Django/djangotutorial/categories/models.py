from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=150, unique=True)
    image = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
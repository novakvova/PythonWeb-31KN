from django.shortcuts import render

from .models import Category


# Create your views here.

def category_list(request):
    # Читаємо список категорій і їх сортуємо
    categories = Category.objects.all().order_by("name")
    # Передаємо список категорій на category_list
    return render(request, "categories/category_list.html", {"categories": categories})

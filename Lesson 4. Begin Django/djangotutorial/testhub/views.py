from django.db.models import Count, Sum
from django.shortcuts import render

from .models import Test


def test_list(request):
    # Читаємо всі тести з БД, додаємо кількість питань і суму балів,
    # нові тести показуємо першими
    tests = (
        Test.objects
        .annotate(
            questions_count=Count("questions"),
            total_points=Sum("questions__points"),
        )
        .order_by("-created_at")
    )
    return render(request, "testhub/test_list.html", {"tests": tests})

from django.db.models import Count,Sum
from django.shortcuts import render

from .models import Test


# Create your views here.
def test_list(request):
    tests = (
        Test.objects
        .annotate(
            questions_count=Count('questions'),
            total_points = Sum('questions__points'),
        )
        .order_by('-created_at')
    )
    return render(request, 'testhub/test_list.html', {'tests': tests})
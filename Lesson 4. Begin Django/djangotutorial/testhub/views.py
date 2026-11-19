from django.db.models import Count,Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import TestStartForm
from .models import Test


# Ключ сесії, де зберігаються id результатів, які цей відвідувач може переглядати
RESULTS_SESSION_KEY = "testhub_results"


def _attempt_key(test_id):
    """Ключ сесії з даними поточної спроби (ПІБ + час початку)."""
    return f"testhub_attempt_{test_id}"

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

def test_start(request, test_id):
    # Крок 1: вводимо ПІБ, після чого запускається таймер
    test = get_object_or_404(Test, pk=test_id, is_active=True)

    if request.method == "POST":
        form = TestStartForm(request.POST)
        if form.is_valid():
            request.session[_attempt_key(test.id)] = {
                **form.cleaned_data,
                "started_at": timezone.now().isoformat(),
            }
            return redirect("testhub:take", test_id=test.id)
    else:
        form = TestStartForm()

    return render(request, "testhub/test_start.html", {
        "test": test,
        "form": form,
        "questions_count": test.questions.count(),
    })
from datetime import datetime, timedelta

from django.db.models import Count,Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import TestStartForm, TestTakeForm
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

def test_take(request, test_id):
    #Якщо по даному test_id не знайдемо тест, то видаємо 404
    test = get_object_or_404(Test, pk=test_id, is_active=True)
    # із сесії отримуємо інфомрацію про людину, яка розпочала тест
    attempt = request.session[_attempt_key(test.id)]
    if not attempt:
        #Спроба пройти тест не розпочата - повертаємося до введення ПІБ
        return redirect("testhub:start", test_id=test.id)

    started_at = datetime.fromisoformat(attempt["started_at"])
    deadline =  started_at + timedelta(minutes=test.time_limit)
    questions = test.questions.prefetch_related("options").order_by("order","id")

    form = TestTakeForm(questions=questions)
    seconds_left = max(0, int((deadline - timezone.now()).total_seconds()))
    return render(request, "testhub/test_take.html", {
        "test": test,
        "form": form,
        "seconds_left": seconds_left,
    })


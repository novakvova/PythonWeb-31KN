from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import TestStartForm, TestTakeForm
from .models import Test, TestResult, TestResultAnswer

# Ключ сесії, де зберігаються id результатів, які цей відвідувач може переглядати
RESULTS_SESSION_KEY = "testhub_results"


def _attempt_key(test_id):
    """Ключ сесії з даними поточної спроби (ПІБ + час початку)."""
    return f"testhub_attempt_{test_id}"


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
    # Крок 2: відповіді на питання
    test = get_object_or_404(Test, pk=test_id, is_active=True)

    attempt = request.session.get(_attempt_key(test.id))
    if not attempt:
        # Спроба не розпочата (або вже завершена) — повертаємо до введення ПІБ
        return redirect("testhub:start", test_id=test.id)

    started_at = datetime.fromisoformat(attempt["started_at"])
    deadline = started_at + timedelta(minutes=test.time_limit)
    questions = test.questions.prefetch_related("options").order_by("order", "id")

    if request.method == "POST":
        form = TestTakeForm(request.POST, questions=questions)
        if form.is_valid():
            result = _save_result(test, attempt, started_at, form.selected_options())
            # Спроба завершена: прибираємо її, щоб повторна відправка не створила дубль
            del request.session[_attempt_key(test.id)]
            allowed = request.session.get(RESULTS_SESSION_KEY, [])
            request.session[RESULTS_SESSION_KEY] = allowed + [result.id]
            return redirect("testhub:result", result_id=result.id)
    else:
        form = TestTakeForm(questions=questions)

    seconds_left = max(0, int((deadline - timezone.now()).total_seconds()))
    return render(request, "testhub/test_take.html", {
        "test": test,
        "form": form,
        "seconds_left": seconds_left,
    })


@transaction.atomic
def _save_result(test, attempt, started_at, selected):
    correct = sum(1 for o in selected.values() if o is not None and o.is_correct)
    # Питання без відповіді теж рахуються як неправильні
    wrong = len(selected) - correct

    result = TestResult.objects.create(
        test=test,
        last_name=attempt["last_name"],
        first_name=attempt["first_name"],
        middle_name=attempt.get("middle_name") or None,
        correct_answers_count=correct,
        wrong_answers_count=wrong,
        started_at=started_at,
        finished_at=timezone.now(),
    )
    TestResultAnswer.objects.bulk_create([
        TestResultAnswer(test_result=result, selected_answer=o, is_correct=o.is_correct)
        for o in selected.values() if o is not None
    ])
    return result


def test_result(request, result_id):
    # Результат бачить лише той, хто проходив тест (id збережено в його сесії)
    if result_id not in request.session.get(RESULTS_SESSION_KEY, []):
        return redirect("testhub:list")

    result = get_object_or_404(TestResult.objects.select_related("test"), pk=result_id)
    chosen = {
        a.selected_answer.question_id: a
        for a in result.answers.select_related("selected_answer")
    }

    rows = []
    score = max_score = 0
    for question in result.test.questions.prefetch_related("options").order_by("order", "id"):
        answer = chosen.get(question.id)
        is_correct = bool(answer and answer.is_correct)
        max_score += question.points
        if is_correct:
            score += question.points
        rows.append({
            "question": question,
            "selected": answer.selected_answer if answer else None,
            "is_correct": is_correct,
            "correct_options": [o for o in question.options.all() if o.is_correct],
        })

    duration = result.finished_at - result.started_at
    return render(request, "testhub/test_result.html", {
        "result": result,
        "rows": rows,
        "score": score,
        "max_score": max_score,
        "duration_minutes": int(duration.total_seconds() // 60),
        "duration_seconds": int(duration.total_seconds() % 60),
    })

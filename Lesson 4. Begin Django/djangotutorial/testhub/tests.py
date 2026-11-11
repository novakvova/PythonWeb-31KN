from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Test, Question, AnswerOption, TestResult


class TestTakingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test = Test.objects.create(title="Основи Python", time_limit=10)
        cls.q1 = Question.objects.create(test=cls.test, text="2+2?", points=1, order=1)
        cls.q1_right = AnswerOption.objects.create(question=cls.q1, text="4", is_correct=True)
        cls.q1_wrong = AnswerOption.objects.create(question=cls.q1, text="5")
        cls.q2 = Question.objects.create(test=cls.test, text="print?", points=2, order=2)
        cls.q2_right = AnswerOption.objects.create(question=cls.q2, text="print()", is_correct=True)
        cls.q2_wrong = AnswerOption.objects.create(question=cls.q2, text="input()")

    def start(self):
        return self.client.post(
            reverse("testhub:start", args=[self.test.id]),
            {"last_name": "Шевченко", "first_name": "Тарас"},
        )

    def test_list_shows_take_button(self):
        response = self.client.get(reverse("testhub:list"))
        self.assertContains(response, reverse("testhub:start", args=[self.test.id]))

    def test_start_requires_name(self):
        response = self.client.post(reverse("testhub:start", args=[self.test.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_take_without_start_redirects(self):
        response = self.client.get(reverse("testhub:take", args=[self.test.id]))
        self.assertRedirects(response, reverse("testhub:start", args=[self.test.id]))

    def test_inactive_test_returns_404(self):
        self.test.is_active = False
        self.test.save()
        response = self.client.get(reverse("testhub:start", args=[self.test.id]))
        self.assertEqual(response.status_code, 404)

    def test_take_page_hides_correct_answers(self):
        self.assertRedirects(self.start(), reverse("testhub:take", args=[self.test.id]))
        response = self.client.get(reverse("testhub:take", args=[self.test.id]))
        self.assertContains(response, "2+2?")
        self.assertNotContains(response, "is_correct")

    def test_full_flow_saves_result(self):
        self.start()
        response = self.client.post(reverse("testhub:take", args=[self.test.id]), {
            f"question_{self.q1.id}": self.q1_right.id,
            f"question_{self.q2.id}": self.q2_wrong.id,
        })
        result = TestResult.objects.get()
        self.assertRedirects(response, reverse("testhub:result", args=[result.id]))
        self.assertEqual(result.correct_answers_count, 1)
        self.assertEqual(result.wrong_answers_count, 1)
        self.assertEqual(result.answers.count(), 2)

        page = self.client.get(reverse("testhub:result", args=[result.id]))
        self.assertEqual(page.context["score"], 1)
        self.assertEqual(page.context["max_score"], 3)

        # Повторна відправка не створює дубль — спроба вже закрита
        self.client.post(reverse("testhub:take", args=[self.test.id]), {})
        self.assertEqual(TestResult.objects.count(), 1)

    def test_unanswered_counts_as_wrong(self):
        self.start()
        self.client.post(reverse("testhub:take", args=[self.test.id]), {})
        result = TestResult.objects.get()
        self.assertEqual(result.correct_answers_count, 0)
        self.assertEqual(result.wrong_answers_count, 2)
        self.assertEqual(result.answers.count(), 0)

    def test_option_from_other_question_rejected(self):
        self.start()
        response = self.client.post(reverse("testhub:take", args=[self.test.id]), {
            f"question_{self.q1.id}": self.q2_right.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TestResult.objects.exists())

    def test_result_hidden_from_other_visitors(self):
        result = TestResult.objects.create(
            test=self.test, last_name="Інший", first_name="Хтось",
            started_at=timezone.now() - timedelta(minutes=1), finished_at=timezone.now(),
        )
        response = self.client.get(reverse("testhub:result", args=[result.id]))
        self.assertRedirects(response, reverse("testhub:list"))

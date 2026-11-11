from django.db import models

# Create your models here.

# Модель тесту
class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_limit = models.PositiveIntegerField(default=30)  # Час у хвилинах
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# Модель питання
class Question(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    text = models.TextField()
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text[:100]

# Модель варіанта відповіді
class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options"
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

#Результати тесту
class TestResult(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="results"
    )

    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)

    correct_answers_count = models.PositiveIntegerField(default=0)
    wrong_answers_count = models.PositiveIntegerField(default=0)

    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()

    def __str__(self):
        return f"{self.last_name} {self.first_name} - {self.test.title}"

class TestResultAnswer(models.Model):
    test_result = models.ForeignKey(
        TestResult,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    selected_answer = models.ForeignKey(
        AnswerOption,
        on_delete=models.CASCADE,
        related_name="test_results"
    )

    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.test_result} - {self.selected_answer.text}"
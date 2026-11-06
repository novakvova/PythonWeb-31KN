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
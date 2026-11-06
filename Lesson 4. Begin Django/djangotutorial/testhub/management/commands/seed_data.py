
from django.core.management.base import BaseCommand
from django.db import transaction

from testhub.models import Test, Question, AnswerOption


class Command(BaseCommand):
    help = "Create seed data for TestHub"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        # Список тестів та питань
        seed_data = [
            {
                "title": "Основи Python",
                "description": "Перевірка базових знань мови Python",
                "time_limit": 15,
                "questions": [
                    {
                        "text": "Яка функція використовується для виведення інформації?",
                        "points": 1,
                        "options": [
                            ("input()", False),
                            ("print()", True),
                            ("type()", False),
                            ("len()", False),
                        ]
                    },
                    {
                        "text": "Який тип даних використовується для цілого числа?",
                        "points": 1,
                        "options": [
                            ("str", False),
                            ("float", False),
                            ("int", True),
                            ("bool", False),
                        ]
                    },
                ]
            },
            {
                "title": "Основи Django",
                "description": "Перевірка знань Django Framework",
                "time_limit": 20,
                "questions": [
                    {
                        "text": "Що означає абревіатура MVT у Django?",
                        "points": 2,
                        "options": [
                            ("Model View Template", True),
                            ("Model Virtual Table", False),
                            ("Main View Template", False),
                            ("Module View Type", False),
                        ]
                    },
                    {
                        "text": "У якому файлі Django описують моделі?",
                        "points": 1,
                        "options": [
                            ("views.py", False),
                            ("urls.py", False),
                            ("models.py", True),
                            ("admin.py", False),
                        ]
                    },
                ]
            },
            {
                "title": "Основи баз даних",
                "description": "Перевірка знань SQL та реляційних баз даних",
                "time_limit": 15,
                "questions": [
                    {
                        "text": "Яка команда SQL використовується для отримання даних?",
                        "points": 1,
                        "options": [
                            ("INSERT", False),
                            ("UPDATE", False),
                            ("DELETE", False),
                            ("SELECT", True),
                        ]
                    },
                    {
                        "text": "Що таке первинний ключ (Primary Key)?",
                        "points": 2,
                        "options": [
                            ("Поле для сортування записів", False),
                            ("Унікальний ідентифікатор запису", True),
                            ("Поле для зберігання пароля", False),
                            ("Зовнішній ключ іншої таблиці", False),
                        ]
                    },
                ]
            },
        ]

        # Створюємо тести, питання та відповіді
        for test_data in seed_data:

            test, created = Test.objects.update_or_create(
                title=test_data["title"],
                defaults={
                    "description": test_data["description"],
                    "time_limit": test_data["time_limit"],
                    "is_active": True,
                }
            )

            # Перебираємо питання поточного тесту
            for index, question_data in enumerate(
                test_data["questions"], start=1
            ):

                question, created = Question.objects.update_or_create(
                    test=test,
                    text=question_data["text"],
                    defaults={
                        "points": question_data["points"],
                        "order": index,
                    }
                )

                # Перебираємо варіанти відповідей
                for option_text, is_correct in question_data["options"]:

                    AnswerOption.objects.update_or_create(
                        question=question,
                        text=option_text,
                        defaults={
                            "is_correct": is_correct
                        }
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Test created/updated: {test.title}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed data successfully completed!"
            )
        )

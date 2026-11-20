import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from testhub.models import Test, Question, AnswerOption


# Дані для заповнення лежать поруч із командою у seed_data.json
DATA_FILE = Path(__file__).with_name("seed_data.json")


def load_seed_data():
    with DATA_FILE.open(encoding="utf-8") as f:
        return json.load(f)


class Command(BaseCommand):
    help = "Create seed data for TestHub"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        seed_data = load_seed_data()

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
                for option in question_data["options"]:

                    AnswerOption.objects.update_or_create(
                        question=question,
                        text=option["text"],
                        defaults={
                            "is_correct": option["is_correct"]
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

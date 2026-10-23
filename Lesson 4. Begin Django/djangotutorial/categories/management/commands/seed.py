import io
import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from PIL import Image

from categories.models import Category
from users.utils import save_custom_image  # ЗМІНІТЬ на реальний шлях до вашої функції


CATEGORIES = [
    ("Electronics", "Phones, laptops and gadgets"),
    ("Books", "Fiction, science and education"),
    ("Games", "Board games and video games"),
    ("Music", "Instruments and vinyl records"),
    ("Clothing", "Men's and women's clothing"),
    ("Sport", "Equipment for sport and outdoor"),
]


def make_placeholder():
    """Генерує просте кольорове зображення в пам'яті (без інтернету)."""
    color = tuple(random.randint(50, 220) for _ in range(3))
    img = Image.new("RGB", (600, 600), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


class Command(BaseCommand):
    help = "Заповнює таблицю категорій тестовими даними"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true",
                            help="Видалити всі категорії перед заповненням")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            Category.objects.all().delete()
            self.stdout.write("Старі категорії видалено")

        created_count = 0
        for name, description in CATEGORIES:
            category, created = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "description": description},
            )
            if created:
                category.image = save_custom_image(
                    make_placeholder(), size=(800, 800), folder="medium"
                )
                category.save()
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Створено нових категорій: {created_count}"
        ))
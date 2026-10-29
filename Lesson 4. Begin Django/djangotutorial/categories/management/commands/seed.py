import io
import random

import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from PIL import Image

from categories.models import Category
from users.utils import save_custom_image  # ЗМІНІТЬ на реальний шлях до вашої функції


# (назва, опис, ключові слова для пошуку фото)
CATEGORIES = [
    ("Electronics", "Phones, laptops and gadgets", "laptop,smartphone"),
    ("Books", "Fiction, science and education", "books,library"),
    ("Games", "Board games and video games", "boardgame,videogame"),
    ("Music", "Instruments and vinyl records", "guitar,vinyl"),
    ("Clothing", "Men's and women's clothing", "clothes,fashion"),
    ("Sport", "Equipment for sport and outdoor", "sport,fitness"),
]


def make_placeholder():
    """Запасний варіант: просте кольорове зображення в пам'яті."""
    color = tuple(random.randint(50, 220) for _ in range(3))
    img = Image.new("RGB", (600, 600), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def download_photo(keywords, size=800):
    """Завантажує реальне фото за ключовими словами. Повертає BytesIO."""
    """Завантажує фото з picsum.photos. Повертає BytesIO."""
    url = f"https://picsum.photos/seed/{keywords}/{size}/{size}"
    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    # перевіряємо, що це справді зображення
    Image.open(io.BytesIO(response.content)).verify()

    buf = io.BytesIO(response.content)
    buf.seek(0)
    return buf


def get_image(keywords, stdout):
    try:
        return download_photo(keywords)
    except Exception as e:
        stdout.write(f"  Не вдалося завантажити фото ({keywords}): {e}. "
                     f"Використано заглушку")
        return make_placeholder()


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
        for name, description, keywords in CATEGORIES:
            category, created = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "description": description},
            )
            if created:
                category.image = save_custom_image(
                    get_image(keywords, self.stdout),
                    size=(800, 800),
                    folder="medium",
                )
                category.save()
                created_count += 1
                self.stdout.write(f"  + {name}")

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Створено нових категорій: {created_count}"
        ))
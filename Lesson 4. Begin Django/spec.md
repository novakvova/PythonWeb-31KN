# Специфікація проєкту «Lesson 4. Begin Django»

Навчальний вебзастосунок на Django: реєстрація та вхід користувачів з аватаром, відновлення пароля через email, каталог категорій і модель онлайн-тестування (TestHub).

---

## 1. Технології та залежності

| Компонент | Версія | Призначення |
|---|---|---|
| Python | 3.12 | Мова (за `__pycache__/*.cpython-312.pyc`) |
| Django | 6.1.1 | Вебфреймворк (MVT) |
| psycopg2-binary | 2.9.13 | Драйвер PostgreSQL |
| Pillow | 12.3.0 | Обробка зображень (resize, конвертація у WEBP) |
| asgiref, sqlparse, tzdata | 3.12.1 / 0.6.0 / 2026.3 | Транзитивні залежності Django |
| requests | — (**відсутній у `requirements.txt`**) | Завантаження фото в команді `seed` |
| Bootstrap | 5.3.8 (CDN jsDelivr) | Стилі та верстка шаблонів |

**Інфраструктура**

- **БД:** PostgreSQL у хмарі Neon (`neondb`, AWS us-east-2). Конфігурація SQLite закоментована; файл `db.sqlite3` лишився від попередніх етапів і не використовується.
- **Пошта:** SMTP `smtp.ukr.net:2525`, SSL — для листів відновлення пароля.
- **Середовище розробки:** Windows, PyCharm (`.idea/`), virtualenv `.venv`.

---

## 2. Структура проєкту

```
Lesson 4. Begin Django/
├── README.md, CLAUDE.md, spec.md
├── requirements.txt              # дублюється у djangotutorial/requirements.txt
└── djangotutorial/               # корінь Django-проєкту (тут manage.py)
    ├── manage.py
    ├── mysite/                   # конфігурація проєкту
    │   ├── settings.py
    │   ├── urls.py               # кореневий роутинг + роздача /images/
    │   ├── views.py              # homepage
    │   └── wsgi.py / asgi.py
    ├── templates/                # спільні шаблони
    │   ├── layout.html           # базовий шаблон (navbar, Bootstrap)
    │   └── home.html
    ├── images/                   # завантажені зображення (WEBP)
    │   ├── small/  medium/  large/
    ├── users/                    # автентифікація, кастомний користувач
    │   ├── models.py  forms.py  views.py  urls.py  utils.py
    │   └── templates/            # login, register, password_reset_*
    ├── categories/               # каталог категорій
    │   ├── models.py  views.py  urls.py
    │   ├── management/commands/seed.py
    │   └── templates/categories/category_list.html
    └── testhub/                  # тести / питання / результати
        ├── models.py
        └── management/commands/seed_data.py
```

---

## 3. Застосунки (apps)

### 3.1 `users` — користувачі та автентифікація

**Модель `CustomUser`** (розширює `AbstractUser`, підключена через `AUTH_USER_MODEL = 'users.CustomUser'`):

| Поле | Тип | Опис |
|---|---|---|
| *(успадковані)* | | username, email, first_name, last_name, password … |
| `image_small` | CharField(255), null | Ім'я файлу аватара 300×300 |
| `image_medium` | CharField(255), null | Ім'я файлу 800×800 |
| `image_large` | CharField(255), null | Ім'я файлу 1200×1200 |

**Маршрути** (`/users/`, namespace `users`):

| URL | View | Опис |
|---|---|---|
| `login/` | `user_login` | Вхід (`CustomUserLoginForm` → `authenticate` → `login`) |
| `register/` | `user_register` | Реєстрація з обов'язковим зображенням |
| `logout/` | `user_logout` | Вихід, редирект на `homepage` |
| `password_reset/` | `password_reset_request` | Запит листа з посиланням |
| `password-reset/done/` | `password_reset_done` | «Лист надіслано» |
| `reset/<uidb64>/<token>/` | `password_reset_confirm` | Перевірка токена й встановлення нового пароля |
| `reset/done/` | `password_reset_complete` | «Пароль змінено» |

**Форми** (`forms.py`) — україномовні лейбли, Bootstrap-клас `form-control`:
- `CustomUserCreationForm` — email (унікальний), ім'я, прізвище, зображення, 2 паролі.
- `CustomUserLoginForm` (на базі `AuthenticationForm`).
- `CustomPasswordResetForm` — перевіряє існування email, генерує токен (`default_token_generator`), надсилає HTML + текстовий лист.
- `CustomSetPasswordForm` (на базі `SetPasswordForm`).

### 3.2 `categories` — каталог категорій

**Модель `Category`:** `name` (unique), `description`, `slug` (unique), `image` (ім'я файлу в `images/medium/`).

**Маршрути** (`/categories/`, namespace `categories`): `''` → `category_list` — список, відсортований за назвою.

**Seed-команда** `py manage.py seed [--clear]`: створює 6 категорій (Electronics, Books, Games, Music, Clothing, Sport); фото завантажуються з `picsum.photos`, у разі помилки генерується кольорова заглушка. Ідемпотентна (`get_or_create` за slug), виконується в `transaction.atomic`.

### 3.3 `testhub` — онлайн-тестування

Поки що лише модельний шар (без views/urls/шаблонів).

```
Test ──< Question ──< AnswerOption
  │                        │
  └──< TestResult ──< TestResultAnswer >──┘
```

| Модель | Ключові поля |
|---|---|
| `Test` | title, description, time_limit (хв, за замовч. 30), created_at, is_active |
| `Question` | test (FK, `related_name="questions"`), text, points, order |
| `AnswerOption` | question (FK, `related_name="options"`), text, is_correct |
| `TestResult` | test (FK, `related_name="results"`), ПІБ проходжувача, correct/wrong_answers_count, started_at, finished_at |
| `TestResultAnswer` | test_result (FK, `related_name="answers"`), selected_answer (FK → AnswerOption), is_correct |

Усі FK — `on_delete=CASCADE`. Результат не прив'язаний до `CustomUser`: проходжувач ідентифікується лише ПІБ.

**Seed-команда** `py manage.py seed_data`: 3 тести (Основи Python, Основи Django, Основи баз даних) з питаннями та варіантами; ідемпотентна (`update_or_create`). Опції `--clear` немає (хоч README її згадує).

---

## 4. Основні архітектурні рішення

1. **Класична MVT-архітектура Django з функціональними views.** Class-based views та DRF не використовуються; кожен застосунок має власний `urls.py` з `app_name`, які підключаються в `mysite/urls.py` через `include()`.

2. **Кастомна модель користувача з першого етапу.** `CustomUser` замість стандартного `User`; email записується в `username` при реєстрації, тому вхід фактично відбувається за email.

3. **Власна система зберігання зображень замість `ImageField`/`MEDIA_ROOT`.**
   - `users/utils.py::save_custom_image(file, size, folder)` → Pillow `thumbnail` (зі збереженням пропорцій, LANCZOS) → WEBP (quality 85) → `images/<folder>/<uuid10>.webp`.
   - У БД зберігається лише ім'я файлу (`CharField`), шлях у шаблоні формується вручну: `/images/<folder>/<filename>`.
   - Роздача — `static(settings.IMAGES_URL, document_root=settings.IMAGES_ROOT)`, що працює тільки при `DEBUG=True`.
   - Для аватара генеруються три розміри (small/medium/large); категорії — лише medium.
   - Налаштування `DJANGORESIZED_*` у `settings.py` — залишок, бібліотека не встановлена й не використовується.
   - Наслідок: при видаленні запису файли з диска не видаляються.

4. **Власна реалізація відновлення пароля** замість вбудованих `PasswordResetView` тощо: токени з `default_token_generator`, uid у base64, посилання формується через `request.build_absolute_uri`, HTML-лист з шаблону `password_reset_email.html`.

5. **Шаблони: спільний базовий `layout.html` + шаблони застосунків.** `TEMPLATES.DIRS = [BASE_DIR / 'templates']` і `APP_DIRS = True`. Шаблони `users` лежать без простору імен (`users/templates/login.html`), `categories` — з простором імен (`categories/templates/categories/…`). Навігація використовує жорстко прописані URL, а не `{% url %}`.

6. **Тестові дані через management-команди** (`seed`, `seed_data`) з транзакціями та ідемпотентністю.

7. **Хмарна PostgreSQL (Neon)** як єдина БД для розробки — немає локальної/окремої тестової конфігурації.

8. **Локалізація інтерфейсу — українська** (тексти форм, повідомлення `messages`, листи), хоча `LANGUAGE_CODE = 'en-us'`, `TIME_ZONE = 'UTC'`.

---

## 5. Відомі проблеми та технічний борг

| # | Проблема | Рекомендація |
|---|---|---|
| 1 | Паролі БД і SMTP, `SECRET_KEY` закомічені у `settings.py` | Винести в `.env` (вже в `.gitignore`), змінити скомпрометовані паролі |
| 2 | `requests` відсутній у `requirements.txt` | Додати |
| 3 | `.gitignore` не виключає `__pycache__/`, `db.sqlite3` | Додати правила |
| 4 | Посилання `/users/profile` у navbar веде на неіснуючий маршрут | Реалізувати профіль або прибрати посилання |
| 5 | `admin.py` у всіх застосунках порожні — моделі не зареєстровані в адмінці | Зареєструвати `CustomUser`, `Category`, моделі `testhub` |
| 6 | `testhub` не має views/urls/шаблонів | Наступний етап: проходження тесту та збереження `TestResult` |
| 7 | `tests.py` порожні; тестовий запуск створить БД на віддаленому Neon | Додати тести, окрему (SQLite) конфігурацію для тестів |
| 8 | Файли зображень не видаляються разом із записами | Сигнали `post_delete` або перехід на `ImageField` |
| 9 | `requirements.txt` дублюється у двох місцях | Залишити один |
| 10 | README згадує `seed_data --clear`, якого немає | Додати опцію або виправити README |

---

## 6. Запуск

```
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
pip install requests
cd djangotutorial
py manage.py migrate
py manage.py seed
py manage.py seed_data
py manage.py runserver 9581
```

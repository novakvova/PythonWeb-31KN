# Специфікація проєкту: Lesson 4. Begin Django

## 1. Загальний опис

Навчальний вебзастосунок на Django 6.1 з трьома функціональними модулями: керування користувачами, каталог категорій і система онлайн-тестування. Інтерфейс українською мовою. Проєкт перебуває в стадії розробки: модуль тестування має незавершений сценарій проходження.

## 2. Технологічний стек

| Шар | Технологія | Примітки |
|---|---|---|
| Мова | Python 3 (код створено в CPython 3.14, судячи з `__pycache__/*.cpython-314.pyc`) | README описує запуск через `py` launcher у Windows |
| Фреймворк | Django 6.1.1 | `startproject` згенеровано Django 6.1.1 |
| База даних | PostgreSQL (хмарний Neon, `ep-…aws.neon.tech`, БД `neondb`) | Драйвер `psycopg2-binary` |
| Обробка зображень | Pillow 12.3.0 | Конвертація в WebP, зміна розміру |
| HTTP-клієнт | `requests` | Використовується лише в команді `seed`; **не зафіксовано** в requirements |
| Фронтенд | Django-шаблони + Bootstrap 5.3.8 (CDN jsDelivr) | Без JS-фреймворків і збірки |
| Тестування | Стандартний `django.test` | Тести не написано (файли `tests.py` порожні) |

## 3. Залежності

Файли `requirements.txt` в корені та в `djangotutorial/` ідентичні:

```
asgiref==3.12.1
Django==6.1.1
pillow==12.3.0
psycopg2-binary==2.9.13
sqlparse==0.6.0
tzdata==2026.3
```

- `asgiref`, `sqlparse` — транзитивні залежності Django.
- `tzdata` — база часових зон (потрібна для `TIME_ZONE`/`USE_TZ`, особливо на Windows).
- Віртуальне середовище `.venv/` знаходиться в корені репозиторію і в `.gitignore`.

**Відсутнє:** `requests` (потрібен для `categories`-команди `seed`).

## 4. Структура репозиторію

```
Lesson 4. Begin Django/          ← git-корінь
├── .venv/                       ← віртуальне середовище (не в git)
├── .idea/, .kilo/               ← налаштування IDE/інструментів
├── .gitignore                   ← .idea/, .env, .venv/, __pycache__/
├── README.md                    ← покрокова інструкція встановлення (укр.)
├── requirements.txt
├── CLAUDE.md                    ← інструкції для Claude Code
├── spec.md                      ← цей документ
└── djangotutorial/              ← Django-проєкт (тут manage.py)
    ├── manage.py
    ├── requirements.txt
    ├── db.sqlite3               ← відстежується в git, але не використовується
    ├── mysite/                  ← конфігурація проєкту
    │   ├── settings.py, urls.py, views.py, wsgi.py, asgi.py
    ├── users/                   ← власна модель користувача, реєстрація, відновлення пароля
    ├── categories/              ← модель Category, список, команда seed
    ├── testhub/                 ← тести, питання, варіанти, результати
    ├── templates/               ← спільні шаблони: layout.html, home.html
    └── images/{small,medium,large}/   ← оброблені зображення (WebP)
```

Кожен застосунок має типовий набір: `models.py`, `views.py`, `urls.py`, `forms.py` (де потрібно), `admin.py` (порожній), `migrations/`, `templates/<app>/`.

## 5. Архітектура

### 5.1. Загальна структура

- **Монолітний Django-проєкт** з трьома доменними застосунками, підключеними через `INSTALLED_APPS` і кореневий `mysite/urls.py`.
- **Маршрутизація з просторами імен:** кожен застосунок має `app_name` і підключається через `include()` з окремим префіксом:
  - `admin/` — адмінка Django
  - `users/` — `users:login`, `users:register`, `users:logout`, скидання пароля
  - `categories/` — `categories:list`
  - `tests/` — `testhub:list`, `testhub:start`, `testhub:take`
  - `` — `homepage` (view у `mysite/views.py`)
- **Шаблони:** базовий `layout.html` з навігацією та блоком `title`; сторінки успадковують його.

### 5.2. Модель користувача

- `AUTH_USER_MODEL = 'users.CustomUser'` задано до першої міграції, тобто з початку проєкту.
- `CustomUser(AbstractUser)` додає три поля `image_small`, `image_medium`, `image_large` (шляхи до файлів зображень).
- **Рішення:** email використовується як `username` (`user.username = form.cleaned_data['email']` при реєстрації), вхід виконується за цим значенням.
- Реєстрація: `CustomUserCreationForm` (наслідує `UserCreationForm`) з обов'язковими полями email, ім'я, прізвище, зображення та паролі. Перевірка унікальності email — у `clean_email`.
- Відновлення пароля: власна логіка в `CustomPasswordResetForm.save()` — генерація токена через `default_token_generator`, побудова посилання вручну (`/users/reset/<uid>/<token>/`), відправка через `send_mail` з HTML- і текстовою версією.

### 5.3. Обробка зображень

- Централізована функція `users/utils.py:save_custom_image(image, size, folder)`:
  1. `compress_image` відкриває зображення Pillow, конвертує в RGB, зменшує з збереженням пропорцій (`thumbnail`), зберігає як WebP (quality 85).
  2. Ім'я файлу — перші 10 символів UUID4 + `.webp`.
  3. Файл записується в `settings.IMAGES_ROOT/<folder>/`, у БД зберігається лише ім'я файлу.
- Розміри: `small` 300×300, `medium` 800×800, `large` 1200×1200 (для користувачів); категорії — `medium` 800×800.
- Роздача файлів: `static(settings.IMAGES_URL, document_root=settings.IMAGES_ROOT)` у кореневому `urls.py`. Це **лише для розробки** (`DEBUG = True`).
- Налаштування `DJANGORESIZED_*` у `settings.py` **не використовуються** — залишок від пакета `django-resized`, який не встановлено.

### 5.4. Категорії

- Модель `Category`: `name` (unique), `slug` (unique), `description`, `image` (ім'я файлу). Рядкове представлення — `name`.
- Єдина сторінка — список, відсортований за назвою, з шаблоном `categories/category_list.html`.
- Заповнення: команда `manage.py seed` (`categories/management/commands/seed.py`):
  - шість категорій з описами та ключовими словами;
  - фото завантажується з `picsum.photos/seed/<keywords>/…`; при помилці мережі — генерується кольорова заглушка;
  - ідемпотентність через `get_or_create(slug=…)`; `--clear` видаляє всі категорії;
  - уся команда загорнута в `transaction.atomic`.

### 5.5. Система тестування (testhub)

**Доменна модель:**

```
Test (title, description, time_limit [хв], is_active, created_at)
 └─ Question (text, points, order)
     └─ AnswerOption (text, is_correct)

TestResult (test, last/first/middle name, correct/wrong counts, started_at, finished_at)
 └─ TestResultAnswer (selected_answer → AnswerOption, is_correct)
```

**Потік проходження (сесійний):**

1. `test_list` — список активних тестів із підрахунком питань і сумою балів (`annotate`).
2. `test_start` — форма ПІБ (`TestStartForm`). Після POST дані та `started_at` зберігаються в сесії під ключем `testhub_attempt_<test_id>`.
3. `test_take` — обчислює дедлайн (`started_at + time_limit`), віддає `seconds_left` для таймера. Форма `TestTakeForm` створює динамічно по одному `ChoiceField` на питання (`question_<id>`, радіокнопки, необов'язкові).

**Ключові рішення:**

- Результати не пишуться в БД до завершення тесту; проміжний стан — у сесії. Це дозволяє не створювати записи для незавершених спроб.
- Відповіді необов'язкові, щоб автозавершення за таймером могло відправити неповну форму.
- Перевірка, що обраний варіант належить питанню, виконується `ChoiceField` (через `choices` з `question.options`).

**Відомі недоліки (стан на зараз):**

- `test_take` не має обробника POST — відповіді не зберігаються, `TestResult` не створюється.
- `if not attempt` після `request.session[...]` не спрацює: при відсутній сесії буде `KeyError`, а не редирект.
- `RESULTS_SESSION_KEY` оголошено, але не використовується.
- `test_take` не перевіряє, що час не минув (`seconds_left` може бути 0, але на це ніхто не реагує).
- Адмінка (`admin.py`) для жодного застосунку не налаштована.

### 5.6. Команда seed_data (testhub)

`testhub/management/commands/seed_data.py` створює три тести з питаннями та варіантами відповідей через `update_or_create` (ідемпотентно). Опції `--clear` немає, хоча README її згадує.

## 6. Конфігурація та середовище

| Параметр | Значення | Коментар |
|---|---|---|
| `DEBUG` | `True` | Лише для розробки |
| `ALLOWED_HOSTS` | `[]` | Працює лише з localhost при `DEBUG=True` |
| `LANGUAGE_CODE` | `en-us` | Інтерфейс переважно українською в шаблонах, але мова Django за замовчуванням англійська |
| `TIME_ZONE` / `USE_TZ` | `UTC` / `True` | |
| `STATIC_URL` | `static/` | Немає `STATIC_ROOT`, статика з CDN і застосунків |
| `EMAIL_BACKEND` | SMTP `smtp.ukr.net:2525`, SSL | Для відновлення пароля |
| `DATABASES` | PostgreSQL Neon (хмара) | SQLite-конфігурація закоментована |

**Порти:** `runserver 9581` (за README).

## 7. Безпека та ризики

1. **Секрети в коді.** `SECRET_KEY`, пароль до БД і пароль SMTP захардкоджені в `settings.py`, які версіонуються в git. Потрібно: перенести в змінні середовища (`.env` уже в `.gitignore`), ротувати скомпрометовані паролі.
2. **`DEBUG = True`** і порожній `ALLOWED_HOSTS` — прийнятно лише для локальної розробки.
3. **Роздача медіа через `static()`** — тільки для розробки.
4. **Email як логін** без підтвердження адреси — будь-хто може зареєструватися з чужою поштою.
5. **Скидання пароля:** `reset_link` будується через `request.build_absolute_uri` з жорстко заданим шляхом `/users/reset/…`, а не через `reverse()`. Це працює, але крихко при зміні маршрутів.
6. **Тестова логіка без POST-обробки** (див. 5.5) — функціональна неповнота, а не безпековий дефект, але блокує використання модуля.
7. **Видалення даних:** `seed --clear` видаляє всі категорії в спільній БД.
8. **`db.sqlite3` у git** — зайвий артефакт, варто видалити з відстеження.

## 8. Якість коду та тестування

- Тести відсутні: усі `tests.py` містять лише заглушку.
- Лінтери та форматери не налаштовано.
- Коментарі та рядки UI — українською; частина коментарів у `views.py` містить помилки кодування або дублювання (наприклад, подвійний docstring у `download_photo`, `# ЗМІНІТЬ на реальний шлях` в імпортах).
- Є помилки шаблонного коду: `users/forms.py:CustomUserCreationForm` оголошує `password1`/`password2` двічі (через `UserCreationForm` і вручну — однаково, але зайве); `users/views.py:user_login` має `print(...)` для налагодження; `user_register` при невалідній формі викликає `messages.success` замість `error`.
- Порожні `admin.py` у всіх застосунках.

## 9. Рекомендовані наступні кроки

1. Перенести секрети в `.env` / змінні середовища, ротувати паролі.
2. Реалізувати POST-обробку `test_take` і створення `TestResult` / `TestResultAnswer` з підрахунком балів; виправити перевірку `attempt` (`session.get(...)`).
3. Додати тести: моделі, `save_custom_image`, сценарії `test_take`, реєстрація, скидання пароля.
4. Зареєструвати моделі в `admin.py`.
5. Додати `requests` до requirements або прибрати залежність з `seed`.
6. Видалити `db.sqlite3` з git і прибрати невикористовувані `DJANGORESIZED_*` та `RESULTS_SESSION_KEY`.
7. Для продакшну: `DEBUG = False`, `ALLOWED_HOSTS`, `STATIC_ROOT`, окрема роздача медіа.

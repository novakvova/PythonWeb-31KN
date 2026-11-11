# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context

This is one lesson folder ("Lesson 4. Begin Django") inside a larger course repo (`PythonWeb-31KN`, git root is the parent directory). It is a teaching project: code comments, UI text, form labels and validation messages are in Ukrainian — keep new user-facing strings in Ukrainian to match. Windows is the dev environment (`py` launcher, `.venv\Scripts\activate.bat`).

## Commands

All `manage.py` commands run from `djangotutorial/` with the venv in this folder activated.

```
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
pip install requests            # needed by the categories seed command, not in requirements.txt

cd djangotutorial
py manage.py migrate
py manage.py runserver 9581     # port 9581 is the convention used in README

py manage.py makemigrations <app>
py manage.py seed [--clear]     # categories: downloads images from picsum.photos (falls back to a placeholder)
py manage.py seed_data          # testhub: tests/questions/answers (no --clear option despite README)

py manage.py test                          # all tests
py manage.py test users.tests.SomeTest.test_x   # single test
```

`tests.py` files are currently empty stubs. Note that `DATABASES` points at a remote Neon PostgreSQL instance (SQLite config is commented out), so migrations, seeds and the test DB all hit that remote server.

## Architecture

Django 6.1 project `mysite` with three apps: `users`, `categories`, `testhub`.

- **Templates**: project-level `templates/layout.html` (Bootstrap 5 via CDN, `{% block title %}` / `{% block content %}`) is the base all pages extend; `templates/home.html` is rendered by `mysite/views.py::homepage`. App templates live in each app's `templates/` dir — note `users` templates are *not* namespaced (`users/templates/login.html`), while `categories` uses `categories/templates/categories/...`.
- **Custom user**: `AUTH_USER_MODEL = 'users.CustomUser'` (extends `AbstractUser`). Registration sets `username = email`, so login is by email. Always use `get_user_model()` / `users.models.CustomUser`, not `django.contrib.auth.models.User`.
- **Image handling (custom, not Django FileField/MEDIA)**: images are stored as plain filename strings in `CharField`s (`CustomUser.image_small/medium/large`, `Category.image`). `users/utils.py::save_custom_image(file, size, folder)` resizes with Pillow, converts to WEBP, writes to `IMAGES_ROOT/<folder>/<uuid>.webp` (`djangotutorial/images/{small,medium,large}`) and returns only the filename. Files are served at `IMAGES_URL = '/images/'` via `static()` in `mysite/urls.py`, so templates build URLs as `/images/<folder>/<filename>`. The `DJANGORESIZED_*` settings are leftovers and not used by this code path.
- **Password reset** is hand-rolled in `users` (custom forms/views, not Django's built-in auth views): `CustomPasswordResetForm.save()` builds the link with `default_token_generator` and sends HTML mail via the SMTP settings in `settings.py`; URLs are namespaced `users:*`.
- **URL namespaces**: `users` and `categories` define `app_name`; root `''` is named `homepage` (used in redirects).
- **testhub**: models only so far — `Test → Question → AnswerOption`, plus `TestResult` (taker's name, counts, start/finish times) and `TestResultAnswer`. It has no `urls.py` and is not included in `mysite/urls.py`; data comes only from `seed_data` (no app registers its models in `admin.py`).

See `spec.md` for the full project specification and known tech-debt list.

## Coding rules

- Follow the existing style: function-based views, forms in `forms.py` with Ukrainian `label`s and `attrs={'class': 'form-control'}` widgets, Ukrainian `messages.*` texts and comments.
- Redirect by URL name (`redirect('homepage')`, `redirect('users:login')`), never by hard-coded path. In new templates use `{% url 'app:name' %}` instead of literal paths like `/users/login/`.
- New pages extend `layout.html` and fill `{% block title %}` / `{% block content %}`; use Bootstrap 5 classes, no custom CSS frameworks.
- Put app templates under a namespaced dir: `<app>/templates/<app>/<name>.html` (the un-namespaced `users` templates are legacy — don't copy that pattern).
- Reference the user model via `get_user_model()` or `settings.AUTH_USER_MODEL` in FKs.
- Images: use `users.utils.save_custom_image()` and store the returned filename in a `CharField`; don't introduce `ImageField`/`MEDIA_ROOT` unless migrating the whole scheme.
- Secrets (DB, SMTP, `SECRET_KEY`) must not be added to `settings.py` as literals — read them from environment / `.env`.
- Any new third-party package goes into `requirements.txt` with a pinned version.

## Architecture rules

- One concern per app; each app owns `urls.py` with `app_name` and is mounted in `mysite/urls.py` via `include()`. Add new apps to `INSTALLED_APPS`.
- Keep views thin: validation in forms (`clean_*`), reusable logic in module helpers (like `users/utils.py`), not in templates.
- Every model change needs a migration (`makemigrations <app>`) committed together with the model; never edit applied migrations.
- Seed data lives in `<app>/management/commands/`, runs inside `@transaction.atomic`, and must be idempotent (`get_or_create` / `update_or_create`); add a `--clear` flag when deleting is useful.
- Register new models in the app's `admin.py`.
- Use `related_name` on every FK (existing convention: `questions`, `options`, `results`, `answers`).

## Testing rules

- Tests go in each app's `tests.py` (or a `tests/` package) using `django.test.TestCase` and `self.client`; run with `py manage.py test <app>`.
- Tests must not run against the remote Neon database. Before adding tests, add a SQLite override for test runs in `settings.py` (e.g. switch `DATABASES` when `'test' in sys.argv`).
- The Django test runner already swaps `EMAIL_BACKEND` to locmem, so assert on `django.core.mail.outbox` (e.g. for password reset); never bypass this to send real mail.
- Tests that save images must point `IMAGES_ROOT` at a temp dir (`@override_settings(IMAGES_ROOT=tempfile.mkdtemp())`) and use an in-memory Pillow image, not files from `images/`.
- Seed commands that download from the network (`seed`) should be tested with `requests.get` mocked.
- Minimum coverage for a new feature: happy path, form validation errors, and access for anonymous vs. logged-in users.

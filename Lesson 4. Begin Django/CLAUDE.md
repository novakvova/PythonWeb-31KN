# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Використовуй короткі відповіді, без зайвого коду, лише важлива інформація!
Перед рефакторингом і роботою з кодом завжди читай файл @spec.md

## Layout

The git root holds the virtualenv (`.venv/`) and README; the Django project lives in `djangotutorial/` (where `manage.py` is). Run all `manage.py` commands from `djangotutorial/`. UI text and comments are in Ukrainian, so keep new user-facing strings consistent with that.

## Commands

Windows, from the git root activate the venv first: `.venv\Scripts\activate.bat`. Then:

```
cd djangotutorial
py manage.py runserver 9581          # README uses port 9581
py manage.py makemigrations <app>
py manage.py migrate
py manage.py test                    # all apps
py manage.py test testhub.tests.SomeTestCase.test_name   # single test
py manage.py seed                    # categories app (see warnings)
py manage.py seed_data               # testhub app (see warnings)
```

There is no linter or formatter configured. The `tests.py` files in every app are still empty stubs, so `manage.py test` currently runs zero tests.

Dependencies are pinned in both `requirements.txt` (root) and `djangotutorial/requirements.txt`: Django 6.1.1, Pillow, psycopg2-binary. `requests` is imported by the `categories` seed command but is not pinned anywhere.

## Warnings

- **The database is a remote Neon PostgreSQL instance**, configured directly in `mysite/settings.py`, not local. `migrate`, `seed` and `seed_data` all write to that shared DB. `db.sqlite3` is tracked in git but is not used by the current settings.
- `seed --clear` deletes every `Category` row before reseeding. `seed` and `seed_data` also download or generate images into `djangotutorial/images/`.
- `settings.py` contains hardcoded `SECRET_KEY`, DB credentials and SMTP credentials. Don't copy them into new code, logs or commits; move them to environment variables if you touch that file.

## Architecture

The project is a Django 6.1 site made of four apps wired in `mysite/urls.py`:

- `users` — custom auth user (`AUTH_USER_MODEL = 'users.CustomUser'`) with three image-path fields. Registration uses the email as `username`, and login authenticates on that username. Password reset sends mail through the SMTP settings in `settings.py` and builds reset links manually in `CustomPasswordResetForm.save`.
- `categories` — a single `Category` model (name, slug, description, image filename) with a list view and the `seed` command.
- `testhub` — quiz engine: `Test` → `Question` → `AnswerOption`, plus `TestResult` / `TestResultAnswer` for recording attempts.
- `mysite` — project settings, root URLconf, and the homepage view.

### Image pipeline (cross-app)

`users/utils.py:save_custom_image` converts an upload to WebP at a given size and writes it under `settings.IMAGES_ROOT/<folder>/`. Only the bare filename is stored in the model's CharField. The `small`, `medium` and `large` folders are used at different sizes. `mysite/urls.py` serves `IMAGES_ROOT` at `/images/` via `static()`, so the same helper is used by user registration and by the `categories` seed command. Any new image upload should go through this helper.

### Test-taking flow (testhub, work in progress)

The flow is session-based, not stored in the database until the end:

1. `test_start` (GET/POST) collects last/first/middle name via `TestStartForm` and stores it, with `started_at`, in the session under `testhub_attempt_<test_id>`.
2. `test_take` computes the deadline from `test.time_limit` and renders `TestTakeForm`. That form builds one `ChoiceField` per question, named `question_<id>`, and `selected_options()` maps each question to the chosen `AnswerOption`.

Known gaps you will hit: `test_take` has no POST handler yet, so answers are never saved. It also reads `request.session[...]` directly, so a missing attempt raises `KeyError` and the `if not attempt: redirect` branch never runs. `RESULTS_SESSION_KEY` is defined but unused. Creating `TestResult` rows is the intended next step.

Templates are under each app's `templates/<app>/` directory, plus the shared `djangotutorial/templates/` (`layout.html` base, `home.html`). Bootstrap 5.3.8 is loaded from jsDelivr in the layout.

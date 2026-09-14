# Simple Python
```
py --version
py -m venv .venv
.venv\Scripts\activate.bat
python.exe -m pip install --upgrade pip

python -m pip install Django

python -m django --version
py -m django --version

django-admin startproject mysite djangotutorial

cd djangotutorial

py manage.py runserver 9581
```

## Перегляд списку бібліотек їх збережння та клонування проекту
```
pip freeze
pip freeze > requirements.txt
git clone https://github.com/novakvova/PythonWeb-31KN.git
cd Lesson 4. Begin Django
py -m venv .venv
.venv\Scripts\activate.bat

python.exe -m pip install --upgrade pip
pip install -r requirements.txt
cd djangotutorial
py manage.py migrate
py manage.py runserver 9581
```


# Install PostgreSQL
```
pip install psycopg2-binary
py manage.py migrate
python3 manage.py migrate
```

## Додаю superuser
```
python manage.py createsuperuser
py manage.py createsuperuser
admin
123456
py manage.py runserver 9581
```

## Working users Custom Django
```
py manage.py startapp users
pip install Pillow 
py manage.py makemigrations users
py manage.py migrate
```
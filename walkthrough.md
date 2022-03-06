# Walkthrough

## 1. Let's Setup Django and Django REST

```commandline
pip install Django
pip install djangorestframework
django-admin startproject queries_to_matrices
cd queries_to_matrices
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## 2. Let's Setup a Docker Environment

```commandline
pip freeze > requirements.txt
```

Add `psycopg2-binary` to our reqs:

```text
...
psycopg2-binary>=2.8
```

Change our `settings.py` file to add the PostGres DB:

```python
ALLOWED_HOSTS = ['*']
...
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
        'PORT': 5432
    },
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Create a little startup script to make life easier:

```shell
#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Setup our `Dockerfile` and `docker-compose.yml` for Django at root level
(adapted from here: https://docs.docker.com/samples/django/):

```dockerfile
FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
```

Setup our `docker-compose.yml` at root level:

```yaml
version: "3.3"

services:
  postgres:
    image: postgres
    environment:
      - POSTGRES_NAME=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
  django:
    build: .
    command: ./start-django.sh
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - postgres
```

Run

```commandline
docker-compose up --build
```

## 3. Setup Our Models

We'll set up `Dock`, `CargoShip`, `Container`, and `Item` models with a 
parent child hierarchy

Dock
|-CargoShip
  |-Containers
    |-Item

```python
from django.db import models
from uuid import uuid4


class Dock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    open_time = models.TimeField()
    close_time = models.TimeField()
    max_ships = models.IntegerField()


class CargoShip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    max_idle_time = models.TimeField()
    max_containers = models.IntegerField()
    dock_id = models.ForeignKey(to=Dock, on_delete=models.PROTECT, default=None)


class Container(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    max_items = models.IntegerField()
    cargo_ship_id = models.ForeignKey(to=CargoShip, on_delete=models.PROTECT, default=None)


class Item(models.Model):
    class Category(models.TextChoices):
        AUTOMOBILES = "AUTOMOBILES"
        PRODUCE = "PRODUCE"
        SEAFOOD = "SEAFOOD"
        ELECTRONICS = "ELECTRONICS"

    id = models.UUIDField(primary_key=True, default=uuid4)
    category = models.CharField(choices=Category.choices, max_length=100)
    container_id = models.ForeignKey(to=Container, on_delete=models.PROTECT, default=None)

```
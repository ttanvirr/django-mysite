# Initial Setups for any Django project (Ubuntu or wsl)

## Install python (if still not)

- for ubuntu (wsl)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## Create venv (virtual environment)

- Create a venv inside the project directory

```bash
python3 -m venv .venv
```

- immediately add it to .gitignore file

.gitignore

```
.venv/
```

- Activate venv

```bash
source .venv/bin/activate
```

## Install Django

```bash
python -m pip install Django
pip freeze > requirements.txt
```

- To verify that Django can be seen by Python, type python from your shell. Then at the Python prompt, try
  to import Django:

```bash
python
>>> import django
>>> print(django.get_version())

//output
6.0.6

>>> exit()
```

- Or, run this while activating the venv

```bash
python -m django --version
```

## Create a django project

```bash
django-admin startproject project_core .
```

- This will create a project named 'project_core' and 'manage.py' file inside the current directory

- Run server to test if everything is okay

```bash
python manage.py runserver
```

- ignore the 'unapplied migration' warning for now.

## Database setup for PostgreSQL

- Django comes with `sqlite` db by defalut. But if we want to setup big db engines like PostgreSql, we need to set it up.
- This can be done at the end, but recommended to do at the beginning to avoid any issue

### Install `psycopg` package (https://github.com/psycopg/psycopg/)

- Install following packages in global system (not in venv)

```bash
sudo apt update
sudo apt install libpq5 libpq-dev python3-dev
```

- In the project's venv (activating venv), install following

```bash
pip install "psycopg[c,pool]"
pip freeze > requirements.txt
```

### Create database

- enter postgress psql shell

open wsl

```bash
sudo -u postgres psql
```

Enter password for `sudo`

- Create db for an existing postgres user
- (DON'T FORGET SEMICOLON FOR POSTGRES SHELL COMMANDS)

```psql
CREATE DATABASE <db_name> OWNER <pg_username>;
```

This will grant all privileges to the user by default

- check if the db is created

```psql
\l
```

### Settings file

- Install dj-database-url for convenience (https://pypi.org/project/dj-database-url/)

settings.py

```py
import dj_database_url

# modify
DATABASES = {
    "default": dj_database_url.config(
        default="postgres://<db_owner>:<owner_password>@<port>:5432/<db_name>",
        conn_max_age=600,
    )
}
```

- DELETE `db.sqlite3` file
- Run migrate and runserver. See if everything is okay

- For extra check, check if database tables (auth, etc.) are created.

```bash
psql -U <db_user> -d <db_name>
```

This tables are created based on INSTALLED_APPS listed in settings.py

### Environ variables

- create .env file in the root

```
DEBUG=True
SECRET_KEY=<django_secret_key>
DATABASE_URL=postgres://<db_owner>:<owner_password>@<port>:5432/<db_name>
```

- immediately add .env to .gitignore file

- Generate secret key for django and add it to the .env file

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

- Install `django-environ` in the venv:

```bash
pip install django-environ
pip freeze > requirements.txt
```

- Modify settings.py to use the envs

settings.py

```py
import environ
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Read the .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Use the variables
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

DATABASES = {
    'default': env.db(), # django-environ has dj-database-url built right in!
}
```

- Stop the server, run migrate and server. Check if everything is okay

### Git commit

- As initial setups have completed, do your first commit (optionally push to a github repo)

## (Optional) TailwindCSS and DaisyUI setup for frontend (not for this project)

<!-- ============================END INITIAL DJANGO SETUPS============================== -->

# CREATING the Polls app

- To create your app, make sure you’re in the same directory as manage.py and type this command:

```bash
python manage.py startapp polls
```

That’ll create a directory `polls`

## Write your first view

Open polls/views.py

```py
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
```

This is the most basic view possible in django.

- To access it in a browser, we need to map it to a URL
- create polls/urls.py and open it

```py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
]
```

- The next step is to configure the root URLconf in the project_core to include the URLconf defined in polls

project_core/urls.py

```py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("polls/", include("polls.urls")), #new
    path("admin/", admin.site.urls),
]
```

- We have now wired an index view into the URLconf. Verify it’s working with the following command:

```bash
python manage.py runserver
```

- Go to http://localhost:8000/polls/ in your browser, and you should see the text defined in the index view.

## Creating models

- defining models means defining database layout, with additional metadata.
- The goal is to define your data model in one place and automatically derive things from it.
  This includes the migrations
- In our poll app, we’ll create two models: Question and Choice. Each Choice is associated with a Question.

These concepts are represented by Python classes.

Edit the polls/models.py

```py
from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
```

- Some Field classes have required arguments. `CharField`, for example, requires a `max_length`.
- That `ForeignKey` tells Django that each Choice is related to a single Question. Django supports all the common database relationships: many-to-one, many-to-many, and one-to-one.

## Activating models

With django models, Django is able to:

- Create a database schema (CREATE TABLE statements) for this app.
- Create a Python database-access API for accessing Question and Choice objects.

`But first we need to tell our project that the polls app is installed.`

**Philosophy**

- Django apps are “pluggable”: You can use an app in multiple projects.

To include the app in our project, we need to edit the porject_core/settings.py file and add the dotted path of PollsConfig class to the INSTALLED_APPS setting:

**project_core/settings.py**

```py
INSTALLED_APPS = [
"polls.apps.PollsConfig", #new
"django.contrib.admin",
# others...
]
```

Now Django knows to include the polls app. Let’s run another command:

**terminal**

```bash
python manage.py makemigrations polls
```

- By running makemigrations, you’re telling Django that you’ve made some changes to your models and that you’d like the changes to be stored as a migration.
- new migration file created - `polls/migrations/0001_initial.py`.

**Note**

- you can run `python manage.py check` to check for any problems in your projects without making migrations or touching the database.

Now, run `migrate` to create those model tables in your database:

**terminal**

```bash
python manage.py migrate
```

The _migrate_ command takes all the migrations that haven’t been applied and synchronizes the changes you made to your models with the schema in the database.

**summary**

- Run `python manage.py makemigrations` to create migrations for changes
- Run `python manage.py migrate` to apply those changes to the database.

## Playing with the API

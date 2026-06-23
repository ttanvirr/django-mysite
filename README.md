# Initial Setups for any Django project (Ubuntu or wsl)

## Install python (if still not)

- for ubuntu (wsl)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## venv (virtual environment)

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

Enter password for sudo

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
psql -U <db_user> -d mysite_db
```

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

- Install django-environ in the venv:

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

<!-- ============================END INITIAL DJANGO SETUPS============================== -->

# CREATING the Polls app

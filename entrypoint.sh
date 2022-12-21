#!/bin/bash
#cron -l 2 -f

if [ -z "$DEBUG" ]
then
    echo "DEBUG not found"
    python3 manage.py makemigrations
    python3 manage.py migrate
    #exec python3 manage.py runserver --noreload 0.0.0.0:8080
    exec gunicorn --config ./gunicorn_config.py reporteede.wsgi
else
    echo "DEBUG has the value: $DEBUG"
    python3 manage.py makemigrations
    python3 manage.py migrate
    #exec python3 manage.py runserver 0.0.0.0:8080
    exec gunicorn --config ./gunicorn_config.py reporteede.wsgi --reload
fi
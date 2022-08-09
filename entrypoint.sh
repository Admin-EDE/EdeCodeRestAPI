#!/bin/bash
service cron start
#cron -l 2 -f
if [ -z "$TOMIGRATE"]
then
  echo "not migrate"
else
  echo "to migrate"
  exec python3 manage.py makemigrations
  exec python3 manage.py migrate
fi

if [ -z "$DEBUG" ]
then
    echo "DEBUG not found"
    #exec gunicorn --config ./gunicorn_config.py controller:app
    exec python3 manage.py runserver --noreload 0.0.0.0:8080
else
    echo "DEBUG has the value: $DEBUG"
    #exec gunicorn --config ./gunicorn_config.py controller:app --reload
    exec python3 manage.py runserver 0.0.0.0:8080
fi
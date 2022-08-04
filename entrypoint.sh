#!/bin/bash
service cron start
#cron -l 2 -f
if [ -z "$DEBUG" ]
then
    echo "DEBUG not found"
    #exec gunicorn --config ./gunicorn_config.py controller:app
    exec python manage.py runserver 0.0.0.0:8080 Debug=False
else
    echo "DEBUG has the value: $DEBUG"
    #exec gunicorn --config ./gunicorn_config.py controller:app --reload
    python manage.py runserver 0.0.0.0:8080 Debug=True
fi
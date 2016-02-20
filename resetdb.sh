#!/bin/sh

rm -r tmdb/migrations ; dropdb tmdb && createdb tmdb && python manage.py makemigrations tmdb && python manage.py migrate && python manage.py add_test_data || exit $?
[ -f credentials.json ] && python manage.py -f credentials.json

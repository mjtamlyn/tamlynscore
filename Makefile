SHELL := /bin/bash

run:
	python manage.py runserver 8001

run-prod:
	gunicorn tamlynscore.wsgi:application -w4 -b 0.0.0.0:1234 --access-logfile -

test:
	python manage.py test

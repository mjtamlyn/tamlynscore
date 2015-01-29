SHELL := /bin/bash

run:
	python manage.py runserver 8001

test:
	python manage.py test

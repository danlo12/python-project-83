
install:
	pip install poetry

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	pip install --user gunicorn
	gunicorn -w 5ma -b 0.0.0.0:$(PORT) page_analyzer:app
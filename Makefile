PORT ?= 8000

install:
	pip install poetry

dev:
	poetry run flask --app page_analyzer:app run

start:
	export PATH=$PATH:/opt/render/.local/bin
	pip install gunicorn
	gunicorn -w 5ma -b 0.0.0.0:$(PORT) page_analyzer:app
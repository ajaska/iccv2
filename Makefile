MAKEFLAGS += --no-builtin-rules 
.SUFFIXES:

.PHONY: all uwsgi uwsgi-dev lint

all: venv

lint: venv/bin/flake8
	venv/bin/flake8 server.py wsgi.py

uwsgi: venv/bin/uwsgi
	venv/bin/uwsgi -i uwsgi.ini --enable-threads

uwsgi-dev: venv/bin/uwsgi
	venv/bin/uwsgi --socket 0.0.0.0:8000 --protocol=http -w wsgi:app -H ./venv

venv:
	virtualenv venv --python=python3
	venv/bin/pip install -r requirements.txt

venv/bin/flake8: venv
	venv/bin/pip install flake8

venv/bin/uwsgi: venv
	venv/bin/pip install uwsgi

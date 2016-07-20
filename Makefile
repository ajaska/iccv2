MAKEFLAGS += --no-builtin-rules 
.SUFFIXES:

.PHONY: all uwsgi lint

all: venv

lint: venv/bin/flake8
	venv/bin/flake8 server.py wsgi.py

uwsgi: venv
	uwsgi -i uwsgi.ini --enable-threads

venv:
	virtualenv venv --python=python3
	venv/bin/pip install -r requirements.txt

venv/bin/flake8: venv
	venv/bin/pip install flake8

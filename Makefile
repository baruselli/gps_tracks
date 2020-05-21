venv: requirements.txt
	test -d venv || ( python -m venv venv) &&	venv\Scripts\activate.bat && pip install -r requirements.txt 

run: venv
	python manage.py migrate && python manage.py runserver 0.0.0.0:8000

run_postgres: venv
	set DB_TYPE=postgres && python manage.py migrate &&	python manage.py runserver 0.0.0.0:8000

run_sqlite: venv
	set DB_TYPE=sqlite && python manage.py migrate && python manage.py runserver 0.0.0.0:8000

makemigrations: venv
	python manage.py makemigrations

migrate: venv
	python manage.py migrate

shell_sqlite: venv
	set DB_TYPE=sqlite && python manage.py shell_plus

shell_postgres: venv
	set DB_TYPE=postgress && python manage.py shell_plus

shell: venv
	python manage.py shell_plus

# quick (no checks on vnev and migrations)
venv_quick: requirements.txt
	venv\Scripts\activate.bat

run_postgres_quick: venv_quick
	set DB_TYPE=postgres &	python manage.py runserver 0.0.0.0:8000

run_sqlite_quick: venv_quick
	set DB_TYPE=sqlite && python manage.py runserver 0.0.0.0:8000

run_quick: venv_quick
	python manage.py runserver 0.0.0.0:8000

shell_sqlite_quick: venv_quick
	set DB_TYPE=sqlite &&	python manage.py shell_plus

shell_postgres_quick: venv_quick
	set DB_TYPE=postgres &&	python manage.py shell_plus

shell_quick: venv_quick
	python manage.py shell_plus


# tests
test_sqlite: venv
	set DB_TYPE=sqlite &&	python manage.py test

test_sqlite_keepdb: venv
	set DB_TYPE=sqlite &&	python manage.py test --keepdb

test_postgres: venv
	set DB_TYPE=postgres &&	python manage.py test

test_postgres_keepdb: venv
	set DB_TYPE=postgres && python manage.py test --keepdb

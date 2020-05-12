call venv\Scripts\activate.bat
start /B chrome http://127.0.0.1:8000/
set DB_TYPE=postgres
call python manage.py migrate
call python manage.py runserver
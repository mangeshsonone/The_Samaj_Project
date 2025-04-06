web: gunicorn the_samaj_project_railway.wsgi --log-file - 
#or works good with external database
web: python manage.py migrate && gunicorn the_samaj_project_railway.wsgi

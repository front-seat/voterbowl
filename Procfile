release: python manage.py migrate --noinput
web: gunicorn --worker-class server.asgi_worker.NoLifespanUvicornWorker --error-logfile=- server.asgi:application

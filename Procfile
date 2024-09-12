web: gunicorn --bind :$PORT app:app
worker: celery -A tasks.celery worker --loglevel=info
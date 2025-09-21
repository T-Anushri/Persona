web: gunicorn app:app
worker: python -m celery worker -A app.celery --loglevel=info
beat: python -m celery beat -A app.celery --loglevel=info

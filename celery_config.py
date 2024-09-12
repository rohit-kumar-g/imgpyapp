from celery import Celery

def make_celery(app):
    print("celery running bro")
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    # celery.conf.update(app.config) //dont use .update
    return celery



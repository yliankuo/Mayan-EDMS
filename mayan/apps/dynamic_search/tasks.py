import logging

from django.apps import apps

from mayan.celery import app

from .runtime import search_backend

logger = logging.getLogger(name=__name__)


@app.task(ignore_result=True)
def task_index_instance(app_label, model_name, object_id):
    #TODO:Add locking
    logger.info('Executing')

    Model = apps.get_model(app_label=app_label, model_name=model_name)
    instance = Model._meta.default_manager.get(pk=object_id)

    search_backend.index_instance(instance=instance)

    logger.info('Finshed')

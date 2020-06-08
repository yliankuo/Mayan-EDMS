import logging

from django.apps import apps

from mayan.apps.lock_manager.exceptions import LockError
from mayan.celery import app

from .literals import TASK_RETRY_DELAY
from .runtime import search_backend

logger = logging.getLogger(name=__name__)


@app.task(bind=True, default_retry_delay=TASK_RETRY_DELAY, max_retries=None, ignore_result=True)
def task_deindex_instance(self, app_label, model_name, object_id):
    logger.info('Executing')

    Model = apps.get_model(app_label=app_label, model_name=model_name)
    instance = Model._meta.default_manager.get(pk=object_id)

    try:
        search_backend.deindex_instance(instance=instance)
    except LockError as exception:
        raise self.retry(exc=exception)

    logger.info('Finshed')


@app.task(bind=True, default_retry_delay=TASK_RETRY_DELAY, max_retries=None, ignore_result=True)
def task_index_instance(self, app_label, model_name, object_id):
    logger.info('Executing')

    Model = apps.get_model(app_label=app_label, model_name=model_name)
    instance = Model._meta.default_manager.get(pk=object_id)

    try:
        search_backend.index_instance(instance=instance)
    except LockError as exception:
        raise self.retry(exc=exception)

    logger.info('Finshed')

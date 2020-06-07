from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_slow

queue_search = CeleryQueue(
    label=_('Search'), name='search', worker=worker_slow
)
queue_search.add_task_type(
    dotted_path='mayan.apps.dynamic_search.tasks.task_index_instance',
    label=_('Index a model instance for searching'),
    name='task_index_instance',
)

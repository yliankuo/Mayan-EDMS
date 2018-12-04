from __future__ import unicode_literals

from django.apps import apps

from .literals import DOCUMENT_IMAGES_CACHE_NAME


def callback_update_cache_size(setting):
    Cache = apps.get_model(app_label='common', model_name='Cache')
    cache = Cache.objects.get(name=DOCUMENT_IMAGES_CACHE_NAME)
    cache.maximum_size = setting.value
    cache.save()


def parse_range(astr):
    # http://stackoverflow.com/questions/4248399/
    # page-range-for-printing-algorithm
    result = set()
    for part in astr.split(','):
        x = part.split('-')
        result.update(range(int(x[0]), int(x[-1]) + 1))
    return sorted(result)

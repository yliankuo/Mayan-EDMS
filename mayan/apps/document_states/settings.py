from __future__ import unicode_literals

import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

namespace = Namespace(name='document_states', label=_('Workflows'))

setting_workflowimagecache_storage = namespace.add_setting(
    global_name='WORKFLOWS_IMAGE_CACHE_STORAGE_BACKEND',
    default='django.core.files.storage.FileSystemStorage', help_text=_(
        'Path to the Storage subclass to use when storing the cached '
        'workflow image files.'
    )
)
setting_workflowimagecache_storage_arguments = namespace.add_setting(
    global_name='WORKFLOWS_IMAGE_CACHE_STORAGE_BACKEND_ARGUMENTS',
    default={'location': os.path.join(settings.MEDIA_ROOT, 'workflows')},
    help_text=_(
        'Arguments to pass to the WORKFLOWS_IMAGE_CACHE_STORAGE_BACKEND.'
    )
)

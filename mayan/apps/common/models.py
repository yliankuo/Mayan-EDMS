from __future__ import unicode_literals

from contextlib import contextmanager
import logging
import uuid

from pytz import common_timezones

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import models, transaction, OperationalError
from django.db.models import Sum
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from lock_manager import LockError
from lock_manager.runtime import locking_backend

from .managers import ErrorLogEntryManager, UserLocaleProfileManager
from .storages import storage_sharedupload

logger = logging.getLogger(__name__)


def upload_to(instance, filename):
    return 'shared-file-{}'.format(uuid.uuid4().hex)


@python_2_unicode_compatible
class Cache(models.Model):
    name = models.CharField(
        max_length=128, unique=True, verbose_name=_('Name')
    )
    label = models.CharField(max_length=128, verbose_name=_('Label'))
    maximum_size = models.PositiveIntegerField(verbose_name=_('Maximum size'))
    storage_instance_path = models.CharField(
        max_length=255, unique=True, verbose_name=_('Storage instance path')
    )

    class Meta:
        verbose_name = _('Cache')
        verbose_name_plural = _('Caches')

    def __str__(self):
        return self.label

    def get_files(self):
        return CachePartitionFile.objects.filter(partition__cache__id=self.pk)

    def get_total_size(self):
        return self.get_files().aggregate(
            file_size__sum=Sum('file_size')
        )['file_size__sum'] or 0

    def prune(self):
        while self.get_total_size() > self.maximum_size:
            self.get_files().earliest().delete()

    def purge(self):
        for partition in self.partitions.all():
            partition.purge()

    @cached_property
    def storage(self):
        return import_string(self.storage_instance_path)


class CachePartition(models.Model):
    cache = models.ForeignKey(
        on_delete=models.CASCADE, related_name='partitions',
        to=Cache, verbose_name=_('Cache')
    )
    name = models.CharField(
        max_length=128, verbose_name=_('Name')
    )

    class Meta:
        unique_together = ('cache', 'name')
        verbose_name = _('Cache partition')
        verbose_name_plural = _('Cache partitions')

    @staticmethod
    def get_combined_filename(parent, filename):
        return '{}-{}'.format(parent, filename)

    @contextmanager
    def create_file(self, filename):
        lock_id = 'cache_partition-create_file-{}-{}'.format(self.pk, filename)
        try:
            logger.debug('trying to acquire lock: %s', lock_id)
            lock = locking_backend.acquire_lock(lock_id)#, LOCK_EXPIRE)
            logger.debug('acquired lock: %s', lock_id)
            try:
                self.cache.prune()

                # Since open "wb+" doesn't create files force the creation of an
                # empty file.
                self.cache.storage.save(
                    name=self.get_full_filename(filename=filename),
                    content=ContentFile(content='')
                )

                try:
                    with transaction.atomic():
                        partition_file = self.files.create(filename=filename)
                        yield partition_file.open(mode='wb')
                        partition_file.update_size()
                except Exception as exception:
                    logger.error(
                        'Unexpected exception while trying to save new '
                        'cache file.'
                    )
                    self.cache.storage.delete(
                        name=self.get_full_filename(filename=filename)
                    )
                    raise
            finally:
                lock.release()
        except LockError:
            logger.debug('unable to obtain lock: %s' % lock_id)
            raise

    def get_file(self, filename):
        try:
            return self.files.get(filename=filename)
        except self.files.model.DoesNotExist:
            return None

    def get_full_filename(self, filename):
        return CachePartition.get_combined_filename(
            parent=self.name, filename=filename
        )

    def purge(self):
        for parition_file in self.files.all():
            parition_file.delete()


class CachePartitionFile(models.Model):
    partition = models.ForeignKey(
        on_delete=models.CASCADE, related_name='files',
        to=CachePartition, verbose_name=_('Cache partition')
    )
    datetime = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Date time')
    )
    filename = models.CharField(max_length=255, verbose_name=_('Filename'))
    file_size = models.PositiveIntegerField(
        db_index=True, default=0, verbose_name=_('File size')
    )

    class Meta:
        get_latest_by = 'datetime'
        unique_together = ('partition', 'filename')
        verbose_name = _('Cache partition file')
        verbose_name_plural = _('Cache partition files')

    def delete(self, *args, **kwargs):
        self.partition.cache.storage.delete(name=self.full_filename)
        return super(CachePartitionFile, self).delete(*args, **kwargs)

    @cached_property
    def full_filename(self):
        return CachePartition.get_combined_filename(
            parent=self.partition.name, filename=self.filename
        )

    def open(self, mode='rb'):
        try:
            return self.partition.cache.storage.open(
                name=self.full_filename, mode=mode
            )
        except Exception as exception:
            logger.error(
                'Unexpected exception opening the cache file; %s', exception
            )
            raise

    def update_size(self):
        self.file_size = self.partition.cache.storage.size(
            name=self.full_filename
        )
        self.save()


class ErrorLogEntry(models.Model):
    """
    Class to store an error log for any object. Uses generic foreign keys to
    reference the parent object.
    """
    namespace = models.CharField(
        max_length=128, verbose_name=_('Namespace')
    )
    content_type = models.ForeignKey(
        blank=True, on_delete=models.CASCADE, null=True,
        related_name='error_log_content_type', to=ContentType,
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey(
        ct_field='content_type', fk_field='object_id',
    )
    datetime = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Date time')
    )
    result = models.TextField(blank=True, null=True, verbose_name=_('Result'))

    objects = ErrorLogEntryManager()

    class Meta:
        ordering = ('datetime',)
        verbose_name = _('Error log entry')
        verbose_name_plural = _('Error log entries')


@python_2_unicode_compatible
class SharedUploadedFile(models.Model):
    """
    Keep a database link to a stored file. Used to share files between code
    that runs out of process.
    """
    file = models.FileField(
        storage=storage_sharedupload, upload_to=upload_to,
        verbose_name=_('File')
    )
    filename = models.CharField(max_length=255, verbose_name=_('Filename'))
    datetime = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Date time')
    )

    class Meta:
        verbose_name = _('Shared uploaded file')
        verbose_name_plural = _('Shared uploaded files')

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        self.filename = force_text(self.file)
        super(SharedUploadedFile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.storage.delete(self.file.name)
        return super(SharedUploadedFile, self).delete(*args, **kwargs)

    def open(self):
        return self.file.storage.open(self.file.name)


@python_2_unicode_compatible
class UserLocaleProfile(models.Model):
    """
    Stores the locale preferences of an user. Stores timezone and language
    at the moment.
    """
    user = models.OneToOneField(
        on_delete=models.CASCADE, related_name='locale_profile',
        to=settings.AUTH_USER_MODEL, verbose_name=_('User')
    )
    timezone = models.CharField(
        choices=zip(common_timezones, common_timezones), max_length=48,
        verbose_name=_('Timezone')
    )
    language = models.CharField(
        choices=settings.LANGUAGES, max_length=8, verbose_name=_('Language')
    )

    objects = UserLocaleProfileManager()

    class Meta:
        verbose_name = _('User locale profile')
        verbose_name_plural = _('User locale profiles')

    def __str__(self):
        return force_text(self.user)

    def natural_key(self):
        return self.user.natural_key()
    natural_key.dependencies = [settings.AUTH_USER_MODEL]

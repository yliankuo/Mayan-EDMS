from __future__ import unicode_literals

from django.utils.encoding import force_text

from rest_framework import serializers
from rest_framework.reverse import reverse

from mayan.apps.common.models import SharedUploadedFile
from mayan.apps.rest_api.relations import MultiKwargHyperlinkedIdentityField
from mayan.apps.rest_api.serializers import LazyExtraFieldsHyperlinkedModelSerializer

from .models import (
    Document, DocumentPage, DocumentType, DocumentTypeFilename,
    DocumentVersion, RecentDocument
)
from .settings import setting_language
from .tasks import task_upload_new_version


class DocumentPageSerializer(serializers.HyperlinkedModelSerializer):
    #document_versions_url = serializers.SerializerMethodField()
    image_url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_page_id',
            },
            {
                'lookup_field': 'document.pk', 'lookup_url_kwarg': 'document_id',
            },
            {
                'lookup_field': 'document_version_id', 'lookup_url_kwarg': 'document_version_id',
            },
        ),
        view_name='rest_api:document_page-image'
    )
    #url = serializers.SerializerMethodField()
    document_version_url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'document_version_id', 'lookup_url_kwarg': 'document_version_id',
            },
            {
                'lookup_field': 'document.pk', 'lookup_url_kwarg': 'document_id',
            }
        ),
        view_name='rest_api:document_version-detail'
    )
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_page_id',
            },
            {
                'lookup_field': 'document.pk', 'lookup_url_kwarg': 'document_id',
            },
            {
                'lookup_field': 'document_version_id', 'lookup_url_kwarg': 'document_version_id',
            },
        ),
        view_name='rest_api:document_page-detail'
    )

    class Meta:
        fields = ('document_version_url', 'image_url', 'page_number', 'url')
        #fields = ('document_version_url', 'page_number', 'url')
        model = DocumentPage

    """
    def get_document_versions_url(self, instance):
        return reverse(
            viewname='rest_api:documentversion-detail', kwargs={
                'document_id': instance.document.pk,
                'document_version_id': instance.document_version.pk
            }, request=self.context['request'], format=self.context['format']
        )

    def get_image_url(self, instance):
        return reverse(
            viewname='rest_api:documentpage-image', kwargs={
                'document_id': instance.document.pk,
                'document_version_id': instance.document_version.pk,
                'document_page_id': instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            viewname='rest_api:documentpage-detail', kwargs={
                'document_id': instance.document.pk,
                'document_version_id': instance.document_version.pk,
                'document_page_id': instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )
    """

class DocumentTypeFilenameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTypeFilename
        fields = ('filename',)


class DocumentTypeSerializer(serializers.HyperlinkedModelSerializer):
    documents_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='document_type_id',
        view_name='rest_api:document_type-document-list'
    )
    #documents_count = serializers.SerializerMethodField()
    #filenames = DocumentTypeFilenameSerializer(many=True, read_only=True)

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_type_id',
                'view_name': 'rest_api:document_type-detail'
            }
        }
        fields = (
            'delete_time_period', 'delete_time_unit', 'documents_url',
            #'delete_time_period', 'delete_time_unit',
            #'documents_count', 'id', 'label', 'filenames', 'trash_time_period',
            'id', 'label', 'trash_time_period',
            'trash_time_unit', 'url'
        )
        model = DocumentType

    #def get_documents_count(self, obj):
    #    return obj.documents.count()

"""
class WritableDocumentTypeSerializer(serializers.ModelSerializer):
    documents_url = serializers.HyperlinkedIdentityField(
        lookup_field='pk', lookup_url_kwarg='document_type_id',
        view_name='rest_api:documenttype-document-list'
    )
    documents_count = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_type_id',
                'view_name': 'rest_api:documenttype-detail'
            }
        }
        fields = (
            'delete_time_period', 'delete_time_unit', 'documents_url',
            'documents_count', 'id', 'label', 'trash_time_period',
            'trash_time_unit', 'url'
        )
        model = DocumentType

    def get_documents_count(self, obj):
        return obj.documents.count()
"""

class DocumentVersionSerializer(serializers.HyperlinkedModelSerializer):
    #document_url = serializers.SerializerMethodField()
    #download_url = serializers.SerializerMethodField()
    document_url = serializers.HyperlinkedIdentityField(
        lookup_field='document_id', lookup_url_kwarg='document_id',
        view_name='rest_api:document-detail'
    )
    #pages_url = serializers.SerializerMethodField()

    pages_url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'document_id', 'lookup_url_kwarg': 'document_id',
            },
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_version_id',
            }
        ),
        view_name='rest_api:document_page-list'
    )

    size = serializers.SerializerMethodField()
    #url = serializers.SerializerMethodField()
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_version_id',
            },
            {
                'lookup_field': 'document_id', 'lookup_url_kwarg': 'document_id',
            },
        ),
        view_name='rest_api:document_version-detail'
    )

    class Meta:
        extra_kwargs = {
            #'document': {
            #    'lookup_field': 'pk', 'lookup_url_kwarg': 'document_id',
            #    'view_name': 'rest_api:document-detail'
            #},
            'file': {'use_url': False},
            #'url': {
            #    'view_kwargs': (
            #        {
            #            'lookup_field': 'pk', 'lookup_url_kwarg': 'document_version_id',
            #        },
            #        {
            #            'lookup_field': 'document__pk', 'lookup_url_kwarg': 'document_id',
            #        },
            #    ),
            #    #'lookup_field': 'pk', 'lookup_url_kwarg': 'document_version_id',
            #    'view_name': 'rest_api:document_version-detail'
            #},
        }
        fields = (
            #'checksum', 'comment', 'document_url', 'download_url', 'encoding',
            'checksum', 'comment', 'document_url', 'encoding',
            #'checksum', 'comment', 'encoding',
            'file', 'mimetype', 'pages_url', 'size', 'timestamp', 'url'
            #'file', 'mimetype', 'size', 'timestamp', 'url'
        )
        model = DocumentVersion
        read_only_fields = ('document', 'file', 'size')

    def get_size(self, instance):
        return instance.size

    def build_url_field(self, field_name, model_class):
        """
        Create a field representing the object's own URL.
        """
        field_class = self.serializer_url_field
        field_kwargs = {'kwargs': 1}

        return field_class, field_kwargs

    """
    def get_document_url(self, instance):
        return reverse(
            viewname='rest_api:document-detail', kwargs={
                'document_id': instance.document.pk
            }, request=self.context['request']#, format=self.context['format']
        )

    def get_download_url(self, instance):
        return reverse(
            viewname='rest_api:document_version-download', kwargs={
                'document_id': instance.document.pk,
                'document_version_id': instance.pk
            }, request=self.context['request']#, format=self.context['format']
        )

    def get_pages_url(self, instance):
        return reverse(
            viewname='rest_api:document_version-page-list', kwargs={
                'document_id': instance.document.pk,
                'document_version_id': instance.pk
            }, request=self.context['request']#, format=self.context['format']
        )


    def get_url(self, obj, view_name, request, format):
        print ' obj, view_name, request, format', obj, view_name, request, format
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)
    """
    """

    def get_url(self, instance, *args, **kwargs):
        print ', *args, **kwargs', args, kwargs
        return reverse(
            viewname='rest_api:document_version-detail', kwargs={
                'document_id': instance.document.pk,
                'document_version_id': instance.pk
            }, request=self.context['request']#, format=self.context['format']
        )
    """
"""
class WritableDocumentVersionSerializer(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    pages_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            'file': {'use_url': False},
        }
        fields = (
            'checksum', 'comment', 'document_url', 'download_url', 'encoding',
            'file', 'mimetype', 'pages_url', 'timestamp', 'url'
        )
        model = DocumentVersion
        read_only_fields = ('document', 'file')

    def get_document_url(self, instance):
        return reverse(
            viewname='rest_api:document-detail', kwargs={
                'document_id': instance.document.pk
            }, request=self.context['request'], format=self.context['format']
        )

    def get_download_url(self, instance):
        return reverse(
            viewname='rest_api:documentversion-download', kwargs={
                'document_id': instance.document.pk,
                'document_version_id': instance.pk
            }, request=self.context['request'], format=self.context['format']
        )

    def get_pages_url(self, instance):
        return reverse(
            viewname='rest_api:documentversion-page-list', kwargs={
                'document_id': instance.document.pk,
                'document_version_id': instance.pk
            }, request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            viewname='rest_api:documentversion-detail', kwargs={
                'document_id': instance.document.pk,
                'document_version_id': instance.pk
            }, request=self.context['request'], format=self.context['format']
        )


class NewDocumentVersionSerializer(serializers.Serializer):
    comment = serializers.CharField(allow_blank=True)
    file = serializers.FileField(use_url=False)

    def save(self, document, _user):
        shared_uploaded_file = SharedUploadedFile.objects.create(
            file=self.validated_data['file']
        )

        task_upload_new_version.delay(
            comment=self.validated_data.get('comment', ''),
            document_id=document.pk,
            shared_uploaded_file_id=shared_uploaded_file.pk, user_id=_user.pk
        )
"""

class DeletedDocumentSerializer(serializers.HyperlinkedModelSerializer):
    document_type_label = serializers.SerializerMethodField()
    restore = serializers.HyperlinkedIdentityField(
        lookup_field='pk', lookup_url_kwarg='document_id',
        view_name='rest_api:trasheddocument-restore'
    )

    class Meta:
        extra_kwargs = {
            'document_type': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_type_id',
                'view_name': 'rest_api:documenttype-detail'
            },
            'url': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_id',
                'view_name': 'rest_api:trasheddocument-detail'
            }
        }
        fields = (
            'date_added', 'deleted_date_time', 'description', 'document_type',
            'document_type_label', 'id', 'label', 'language', 'restore',
            'url', 'uuid',
        )
        model = Document
        read_only_fields = (
            'deleted_date_time', 'description', 'document_type', 'label',
            'language'
        )

    def get_document_type_label(self, instance):
        return instance.document_type.label


class HyperlinkedField(serializers.Field):
    """
    Represents the instance, or a property on the instance, using hyperlinking.
    """
    read_only = True

    def __init__(self, *args, **kwargs):
        self.view_name = kwargs.pop('view_name', None)
        # Optionally the format of the target hyperlink may be specified
        self.format = kwargs.pop('format', None)
        # Optionally specify arguments
        self.view_args = kwargs.pop('view_args', None)

        super(HyperlinkedField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        return 'qe'

    def field_to_native(self, obj, field_name):
        return 'qwe'
        request = self.context.get('request', None)
        format = self.context.get('format', None)
        view_name = self.view_name

        # By default use whatever format is given for the current context
        # unless the target is a different type to the source.
        if format and self.format and self.format != format:
            format = self.format

        try:
            return reverse(view_name, args=self.view_args, request=request, format=format)
        except NoReverseMatch:
            pass

        raise Exception('Could not resolve URL for field using view name "%s"' % view_name)


class DocumentSerializer(LazyExtraFieldsHyperlinkedModelSerializer):
    document_type = DocumentTypeSerializer(read_only=True)
    #document_type_url = serializers.HyperlinkedIdentityField(
    #    lookup_field='document_type_id', lookup_url_kwarg='document_type_id',
    #    view_name='rest_api:document_type-detail'
    #)
    latest_version = DocumentVersionSerializer(many=False, read_only=True)
    versions_url = serializers.HyperlinkedIdentityField(
        lookup_field='pk', lookup_url_kwarg='document_id',
        view_name='rest_api:document_version-list'
    )

    class Meta:
        extra_kwargs = {
            'document_type': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_type_id',
                'view_name': 'rest_api:document_type-detail'
            },
            'url': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'document_id',
                'view_name': 'rest_api:document-detail'
            }
        }
        fields = (
            'date_added', 'description', 'document_type', 'id', 'label',
            #'date_added', 'description', 'document_type_url', 'id', 'label',
            'language', 'latest_version', 'url', 'uuid', 'versions_url',
            #'language', 'url', 'uuid', 'versions_url'
        )
        model = Document
        #read_only_fields = ('document_type', 'label')


"""
class WritableDocumentSerializer(serializers.ModelSerializer):
    document_type = DocumentTypeSerializer(read_only=True)
    latest_version = DocumentVersionSerializer(many=False, read_only=True)
    versions = serializers.HyperlinkedIdentityField(
        lookup_field='pk', lookup_url_kwarg='document_id',
        view_name='rest_api:document-version-list'
    )
    url = serializers.HyperlinkedIdentityField(
        lookup_field='pk', lookup_url_kwarg='document_id',
        view_name='rest_api:document-detail',
    )

    class Meta:
        fields = (
            'date_added', 'description', 'document_type', 'id', 'label',
            'language', 'latest_version', 'url', 'uuid', 'versions',
        )
        model = Document
        read_only_fields = ('document_type',)


class NewDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    def save(self, _user):
        document = Document.objects.create(
            description=self.validated_data.get('description', ''),
            document_type=self.validated_data['document_type'],
            label=self.validated_data.get(
                'label', force_text(self.validated_data['file'])
            ),
            language=self.validated_data.get(
                'language', setting_language.value
            )
        )
        document.save(_user=_user)

        shared_uploaded_file = SharedUploadedFile.objects.create(
            file=self.validated_data['file']
        )

        task_upload_new_version.delay(
            document_id=document.pk,
            shared_uploaded_file_id=shared_uploaded_file.pk, user_id=_user.pk
        )

        self.instance = document
        return document

    class Meta:
        fields = (
            'description', 'document_type', 'id', 'file', 'label', 'language',
        )
        model = Document
"""

class RecentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('document', 'datetime_accessed')
        model = RecentDocument

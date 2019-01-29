from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.serializers import DocumentSerializer
from mayan.apps.rest_api.relations import MultiKwargHyperlinkedIdentityField

from .models import Tag
from .permissions import permission_tag_attach


class TagSerializer(serializers.HyperlinkedModelSerializer):
    attach_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='tag_id', view_name='rest_api:tag-document-attach'
    )

    documents_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='tag_id', view_name='rest_api:tag-document-list'
    )

    remove_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='tag_id', view_name='rest_api:tag-document-remove'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'tag_id',
                'view_name': 'rest_api:tag-detail'
            },
        }
        fields = (
            'attach_url', 'color', 'documents_url', 'label', 'id',
            'remove_url', 'url'
        )
        model = Tag



"""
class WritableTagSerializer(serializers.ModelSerializer):
    documents_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of document primary keys to which this tag '
            'will be attached.'
        ), required=False
    )

    class Meta:
        fields = (
            'color', 'documents_pk_list', 'id', 'label',
        )
        model = Tag

    def _add_documents(self, documents_pk_list, instance):
        instance.documents.add(
            *Document.objects.filter(pk__in=documents_pk_list.split(','))
        )

    def create(self, validated_data):
        documents_pk_list = validated_data.pop('documents_pk_list', '')

        instance = super(WritableTagSerializer, self).create(validated_data)

        if documents_pk_list:
            self._add_documents(
                documents_pk_list=documents_pk_list, instance=instance
            )

        return instance

    def update(self, instance, validated_data):
        documents_pk_list = validated_data.pop('documents_pk_list', '')

        instance = super(WritableTagSerializer, self).update(
            instance, validated_data
        )

        if documents_pk_list:
            instance.documents.clear()
            self._add_documents(
                documents_pk_list=documents_pk_list, instance=instance
            )

        return instance
"""

class DocumentTagSerializer(TagSerializer):
    #document_attach_url = serializers.HyperlinkedIdentityField(
    #    lookup_url_kwarg='document_id', view_name='rest_api:document-tag-attach'
    #)

    class Meta(TagSerializer.Meta):
        #fields = TagSerializer.Meta.fields + ('document_attach_url',)
        fields = TagSerializer.Meta.fields
        #fields = TagSerializer.Meta.fields + ('document_tag_url', 'tag_pk')
        #fields = TagSerializer.Meta.fields + ('tag_pk',)
        #read_only_fields = TagSerializer.Meta.fields + ('document_attach_url',)
        read_only_fields = TagSerializer.Meta.fields
        #read_only_fields = TagSerializer.Meta.fields

        #related_models = ('tags',)
        #related_models_kwargs = {
        #    'documents': {
        ##        #'pk_list': 'tags_pk_list', 'model': Tag,
        #        #'model': Tag,
        #        'object_permission': {'create': permission_tag_attach},
        #        #'add_method': 'add', 'add_method_kwargs': 'document'
        #    }
        #}

    '''
    def create(self, validated_data):
        """
        queryset = Tag.objects.filter(pk__in=validated_data['tags_pk_list'].split(','))

        #permission = self.object_permission.get('create')

        #if permission:
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_tag_attach, queryset=queryset,
            user=self.context['request'].user
        )

        for tag in queryset.all():
            tag.attach_to(
                document=self.context['document'],
                user=self.context['request'].user
            )
        """
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_tag_attach, queryset=Tag.objects.all(),
            user=self.context['request'].user
        )
        tag = get_object_or_404(queryset=queryset, pk=validated_data['tag_pk'])
        tag.attach_to(
            document=self.context['document'],
            user=self.context['request'].user
        )
        return tag
        #return None
    '''

    def get_document_tag_url(self, instance):
        return reverse(
            viewname='rest_api:document-tag-detail', kwargs={
                'document_id': self.context['document'].pk,
                'tag_id': instance.pk
            }, request=self.context['request'], format=self.context['format']
        )


class DocumentTagAttachSerializer(serializers.Serializer):
    tags_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of tag primary keys that will be attached '
           'to this document.'
        ), write_only=True
    )


class TagAttachSerializer(serializers.Serializer):
#class TagAttachSerializer(TagSerializer):
    documents_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of document primary keys to which this '
            'tag will be attached.'
        ), write_only=True
    )

    #class Meta(TagSerializer.Meta):
    #    fields = TagSerializer.Meta.fields + ('documents_pk_list',)
    #    read_only_fields = TagSerializer.Meta.fields

    def attach(self, instance):
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_tag_attach, queryset=Document.objects.all(),
            user=self.context['request'].user
        )

        for document in queryset.filter(pk__in=self.validated_data['documents_pk_list'].split(',')):
            instance.attach_to(document=document, user=self.context['request'].user)

        #print '@@@@@@@', self.validated_data['document_pk_list']
        #print '@@@@@@@', instance
        #print '22222', validated_data
        #print '!!!', self.data['document_pk_list']


class TagRemoveSerializer(serializers.Serializer):
    documents_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of document primary keys from which this '
            'tag will be removed.'
        ), write_only=True
    )

    def remove(self, instance):
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_tag_attach, queryset=Document.objects.all(),
            user=self.context['request'].user
        )

        for document in queryset.filter(pk__in=self.validated_data['documents_pk_list'].split(',')):
            instance.remove_from(document=document, user=self.context['request'].user)



class RelatedModel(object):
    @classmethod
    def generate(cls, serializer, validated_data):
        result = []

        kwargs = getattr(serializer.Meta, 'related_model_kwargs', {})
        kwargs.update({'serializer': serializer})

        for field_name in getattr(serializer.Meta, 'related_models', []):
            kwargs.update({'field_name': field_name})
            related_field = cls(**kwargs)
            related_field.pop_pk_list(validated_data=validated_data)
            result.append(related_field)

        return result

    def __init__(self, field_name, serializer, pk_list_field=None, model=None, object_permission=None):
        self.field_name = field_name
        self._pk_list_field = pk_list_field
        self.model = model
        self.object_permission = object_permission
        self.serializer = serializer

    def create(self, instance):
        field = self.get_field(instance=instance)
        field.clear()
        #model = self.get_model()

        queryset = self.get_model().objects.filter(pk__in=self.pk_list.split(','))

        permission = self.object_permission.get('create')

        if permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission,
                queryset=queryset,
                user=self.serializer.context['request'].user
            )

        self.related_add()

        field.add(*queryset)
        #fieldqueryset=queryset)

    #def related_add(self, queryset):
    #    self.get_field().add(*queryset)


    #def _get_m2m_field(self, instance):
    #    getattr(instance, m2m_field_name).all()

    """
    def _add_m2m(self, instance, m2m_pk_list, permission):
        m2m_field = self._get_m2m_field()
        m2m_field.clear()

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission,
            queryset=m2m_model.objects.filter(pk__in=m2m_pk_list.split(',')),
            user=self.context['request'].user
        )

        #m2m_field.add(*queryset)
        self._m2m_add(m2m_field=m2m_field, queryset=queryset)
    """

    def get_model(self):
        return self.model or self.get_field.model

    def get_field(self, instance):
        return getattr(instance, self.field_name)

    def get_pk_list_field_name(self):
        return self._pk_list_field or '{}_pk_list'.format(self.field_name)

    def pop_pk_list(self, validated_data):
        self.pk_list = validated_data.pop(self.get_pk_list_field_name(), '')


class RelatedModelSerializerMixin(object):
    #m2m_pk_list_name = 'documents_pk_list'
    #m2m_field_name = 'documents'
    #m2m_model = Document

    """
    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'tag_pk',
                'view_name': 'rest_api:tag-detail'
            }
        }
        fields = (
            'color', 'documents_count', 'documents_pk_list', 'documents_url',
            'id', 'label', 'url'
        )
        model = Tag
        related_models = ('documents',)
        related_models_kwargs = {
            'documents': {
                'pk_list_field': 'documents_pk_list', 'model': Document,
                'permissions': {'create': permission_tag_attach}
            }
        }
    """

    def _get_m2m_field(self, instance):
        getattr(instance, m2m_field_name).all()

    def _add_m2m(self, instance, m2m_pk_list, permission):
        m2m_field = self._get_m2m_field()
        m2m_field.clear()

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission,
            queryset=m2m_model.objects.filter(pk__in=m2m_pk_list.split(',')),
            user=self.context['request'].user
        )

        #m2m_field.add(*queryset)
        self._m2m_add(m2m_field=m2m_field, queryset=queryset)

    #def _m2m_add(self, m2m_field, queryset):
    #    m2m_field.add(*queryset)

    def _m2m_add(self, m2m_field, queryset):
        for document in queryset.all():
            m2m_field.add(document=document, user=self.context['request'].user)

    def create(self, validated_data):
        related_objects = RelatedModel.generate(
            serializer=self, validated_data=validated_data
        )

        instance = super(RelatedModelSerializerMixin, self).create(
            validated_data=validated_data
        )

        #TODO: return a container class
        #TODO:related_objects.create(instance=instance)
        for related_object in related_objects:
            related_object.create(instance=instance)

        #if m2m_pk_list:
        ##    self._add_m2m(
        #        instance=instance, m2m_pk_list=m2m_pk_list,
        #        permission=permission_tag_add
        #    )

        return instance

        '''
        # Extract the related field data before calling the superclass
        # .create() and avoid an error due to unknown field data.

        #related_models = self.Meta.related_models

        #self.Meta.related_models
        related_models_dictionary = {}
        for related_model in self.Meta.related_models:

            #if self.m2m_pk_list_name:
                m2m_pk_list = validated_data.pop(self.get_related_model_pk_list(), '')

        instance = super(RelatedObjectSerializerMixin, self).create(
            validated_data=validated_data
        )

        if m2m_pk_list:
            self._add_m2m(
                instance=instance, m2m_pk_list=m2m_pk_list,
                permission=permission_tag_add
            )

        return instance
        '''


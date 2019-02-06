from __future__ import absolute_import, unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.serializers import DocumentSerializer
from mayan.apps.rest_api.mixins import ExternalObjectListSerializerMixin

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


class TagDocumentAttachRemoveSerializer(ExternalObjectListSerializerMixin, serializers.Serializer):
    document_id = serializers.CharField(
        help_text=_(
            'Primary key of document to which this tag will be attached or '
            'removed.'
        ), required=False, write_only=True
    )
    documents_id_list = serializers.CharField(
        help_text=_(
            'Comma separated list of document primary keys to which this '
            'tag will be attached or removed.'
        ), required=False, write_only=True
    )

    class Meta:
        external_object_list_model = Document
        external_object_list_permission = permission_tag_attach
        external_object_list_pk_field = 'document_id'
        external_object_list_pk_list_field = 'document_id_list'

    def attach(self, instance):
        queryset = self.get_external_object_list()
        for document in queryset:
            instance.attach_to(document=document, user=self.context['request'].user)

    def remove(self, instance):
        queryset = self.get_external_object_list()
        for document in queryset:
            instance.attach_from(document=document, user=self.context['request'].user)

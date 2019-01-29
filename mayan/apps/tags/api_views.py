from __future__ import absolute_import, unicode_literals

from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.documents.api_views import DocumentViewSet
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.serializers import DocumentSerializer
from mayan.apps.rest_api.filters import MayanObjectPermissionsFilter
from mayan.apps.rest_api.generics import (
    ListAPIView, ListCreateAPIView, RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView
)
from mayan.apps.rest_api.permissions import MayanPermission

from .models import Tag
from .permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)
from .serializers import (
    DocumentTagAttachSerializer, DocumentTagSerializer, TagAttachSerializer,
    TagRemoveSerializer, TagSerializer,
)



from django.conf.urls import url, include
from django.contrib.auth.models import User

from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema


class TagViewSet(viewsets.ModelViewSet):
    filter_backends = (MayanObjectPermissionsFilter,)
    lookup_field = 'pk'
    lookup_url_kwarg='tag_id'
    permission_classes = (MayanPermission,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


    #@swagger_auto_schema(operation_description='GET /articles/today/')
    @swagger_auto_schema(
        operation_description="partial_update description override", responses={200: TagAttachSerializer}
    )
    @action(
        detail=True, lookup_field='pk', lookup_url_kwarg='tag_id',
        methods=('post',), serializer_class=TagAttachSerializer,
        url_name='document-attach', url_path='attach'
    )
    def attach(self, request, *args, **kwargs):
        #print '!!! attach', args, kwargs#, self.context
        #return Response({})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #print '((((((((', serializer.validated_data
        #self.perform_attach(serializer=serializer)
        serializer.attach(instance=self.get_object())
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    #def perform_attach(self, serializer):
    #    #print '!!!!', serializer
    #    serializer.attach(instance=self.get_object())

    #def get_success_headers(self, data):
    #    try:
    #        return {'Location': str(data[api_settings.URL_FIELD_NAME])}
    #    except (TypeError, KeyError):
    #        return {}

    @action(
        detail=True, lookup_field='pk', lookup_url_kwarg='tag_id',
        url_name='document-list', url_path='documents'
    )
    def document_list(self, request, *args, **kwargs):
        queryset = self.get_object().documents.all()

        #TODO:Filter queryset
        #queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            #serializer = self.get_serializer(page, many=True)
            serializer = DocumentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        #serializer = self.get_serializer(queryset, many=True)
        serializer = DocumentSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


        #serializer = DocumentSerializer(
        #    instance=, many=True,
        #    context={'request': request}
        #)
        #return Response(serializer.data)


    @action(
        detail=True, lookup_field='pk', lookup_url_kwarg='tag_id',
        methods=('post',), serializer_class=TagRemoveSerializer,
        url_name='document-remove', url_path='remove'
    )
    def remove(self, request, *args, **kwargs):
        #print '!!! attach', args, kwargs#, self.context
        #return Response({})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #print '((((((((', serializer.validated_data
        #self.perform_attach(serializer=serializer)
        serializer.remove(instance=self.get_object())
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    #def get_serializer_class(self, *args, **kwargs):
    #    #if self.action == 'attach':
    #    print '!!!!get_serializer_class', args, kwargs
    #    return TagAttachSerializer



class DocumentTagViewSet(ExternalObjectMixin, viewsets.ReadOnlyModelViewSet):
    external_object_class = Document
    external_object_pk_url_kwarg = 'document_id'
    external_object_permission = permission_tag_view
    lookup_field = 'pk'
    object_permission = {
        'list': permission_document_view,
        'retrieve': permission_document_view
    }
    serializer_class = DocumentTagSerializer

    @action(
        detail=True, lookup_field='pk', lookup_url_kwarg='document_id',
        methods=('post',), serializer_class=DocumentTagAttachSerializer,
        url_name='tag-attach', url_path='attach'
    )
    def attach(self, request, *args, **kwargs):
        return Response({})


        '''
        serializer = DocumentSerializer(
            instance=self.get_object().documents.all(), many=True,
            context={'request': request}
        )
        return Response(serializer.data)
        '''

    def get_document(self):
        return self.get_external_object()

    def get_queryset(self):
        #return self.get_document().get_tags(user=self.request.user).all()
        return self.get_document().tags.all()

    #@detail_route(lookup_url_kwarg='tag_id')
    #def document_list(self, request, *args, **kwargs):
    #    serializer = DocumentSerializer(
    ##        instance=self.get_object().documents.all(), many=True,
    #        context={'request': request}
    #    )
    #    return Response(serializer.data)

'''

class APITagListView(ListCreateAPIView):
    """
    get: Returns a list of all the tags.
    post: Create a new tag.
    """
    object_permission = {'GET': permission_tag_view}
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    view_permission = {'POST': permission_tag_create}


class APITagView(RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected tag.
    get: Return the details of the selected tag.
    patch: Edit the selected tag.
    put: Edit the selected tag.
    """
    lookup_url_kwarg = 'tag_pk'
    object_permission = {
        'DELETE': permission_tag_delete,
        'GET': permission_tag_view,
        'PATCH': permission_tag_edit,
        'PUT': permission_tag_edit
    }
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

##

class APITagDocumentListView(ExternalObjectMixin, ListCreateAPIView):
    """
    get: Returns a list of all the documents tagged by a particular tag.
    """
    external_object_class = Tag
    external_object_pk_url_kwarg = 'tag_pk'
    external_object_permission = permission_tag_view
    object_permission = {'GET': permission_document_view}
    serializer_class = TagDocumentSerializer

    def get_queryset(self):
        return self.get_tag().get_documents(user=self.request.user).all()

    def get_tag(self):
        return self.get_external_object()

##
'''


'''
class APITagView(RetrieveDestroyAPIView):
    """
    delete: Delete the selected tag document.
    get: Return the details of the selected tag document.
    """
    lookup_url_kwarg = 'tag_pk'
    object_permission = {
        'DELETE': permission_tag_delete,
        'GET': permission_tag_view,
        'PATCH': permission_tag_edit,
        'PUT': permission_tag_edit
    }
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
'''
##
'''
class DocumentSourceMixin(ExternalObjectMixin):
    external_object_class = Document
    external_object_pk_url_kwarg = 'document_pk'
    serializer_class = DocumentTagSerializer

    def get_document(self):
        return self.get_external_object()

    def get_external_object_permission(self):
        permission_dictionary = {
            'DELETE': permission_tag_remove,
            'GET': permission_tag_view,
            'POST': permission_tag_attach
        }

        return permission_dictionary.get(self.request.method)

    def get_queryset(self):
        return self.get_document().tags.all()

    def get_serializer_context(self):
        context = super(DocumentSourceMixin, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'document': self.get_document(),
                }
            )

        return context


class APIDocumentTagListView(DocumentSourceMixin, ListCreateAPIView):
    """
    get: Returns a list of all the tags attached to a document.
    post: Attach a tag to a document.
    """
    #external_object_class = Document
    #external_object_pk_url_kwarg = 'document_pk'
    object_permission = {
        'GET': permission_tag_view,
        #'POST': permission_tag_attach
    }
    #serializer_class = DocumentTagSerializer

    #def get_document(self):
    #    return self.get_external_object()

    #def get_external_object_permission(self):
    #    if self.request.method == 'POST':
    #        return permission_tag_attach
    #    else:
    #        return permission_tag_view

    #def get_queryset(self):
    #    #if self.request.method == 'POST':
    #    #    permission = permission_tag_attach
    #    #else:
    #        #    permission = permission_tag_view
    #
    #    return self.get_document().tags().all()
    #    #return self.get_document().get_tags(
    ##    #    permission=permission, user=self.request.user
    #    #).all()

    """
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIDocumentTagListView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'document': self.get_document(),
                }
            )

        return context
    """

class APIDocumentTagView(DocumentSourceMixin, RetrieveDestroyAPIView):
    """
    delete: Remove a tag from the selected document.
    get: Returns the details of the selected document tag.
    """
    #external_object_class = Document
    #external_object_pk_url_kwarg = 'document_pk'
    lookup_url_kwarg = 'tag_pk'
    mayan_object_permission = {
        'GET': permission_tag_view,
        'DELETE': permission_tag_remove
    }
    #serializer_class = DocumentTagSerializer

    #def get_document(self):
    #    return self.get_external_object()

    #def get_external_object_permission(self):
    #    if self.request.method == 'DELETE':
    #        return permission_tag_remove
    #    else:
    #        return permission_tag_view

    """
    def get_queryset(self):
        if self.request.method == 'DELETE':
            permission = permission_tag_remove
        else:
            permission = permission_tag_view

        return self.get_document().get_tags(
            permission=permission, user=self.request.user
        ).all()
    """

    """
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIDocumentTagView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'document': self.get_document(),
                }
            )

        return context
    """

    def perform_destroy(self, instance):
    #    try:
        from mayan.apps.acls.models import AccessControlList
        from rest_framework.generics import get_object_or_404

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_tag_remove, queryset=Tag.objects.all(),
            user=self.request.user
        )
        instance = get_object_or_404(queryset=queryset, pk=instance.pk)
        #instance.attach_to(
        #    document=self.context['document'],
        #    user=self.context['request'].user
        #)

        instance.remove_from(
            document=self.get_document(), user=self.request.user
        )
        #instance.documents.remove(self.get_document())
    #    except Exception as exception:
    #        raise ValidationError(exception)

    #def retrieve(self, request, *args, **kwargs):
    #    instance = self.get_object()

    #    serializer = self.get_serializer(instance)
    #    return Response(serializer.data)
'''

from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDocumentTagView, APIDocumentTagListView, APITagDocumentListView,
    APITagListView, APITagView
)
from .views import (
    DocumentTagListView, TagAttachActionView, TagCreateView,
    TagDeleteActionView, TagEditView, TagListView, TagRemoveActionView,
    TagTaggedItemListView
)

urlpatterns = [
    url(regex=r'^tags/list/$', name='tag_list', view=TagListView.as_view()),
    url(
        regex=r'^tags/create/$', name='tag_create',
        view=TagCreateView.as_view()
    ),
    url(
        regex=r'^tags/(?P<tag_pk>\d+)/delete/$', name='tag_delete',
        view=TagDeleteActionView.as_view()
    ),
    url(
        regex=r'^tags/(?P<tag_pk>\d+)/edit/$', name='tag_edit',
        view=TagEditView.as_view()
    ),
    url(
        regex=r'^tags/(?P<tag_pk>\d+)/documents/$',
        name='tag_tagged_item_list', view=TagTaggedItemListView.as_view()
    ),
    url(
        regex=r'^tags/multiple/delete/$', name='tag_multiple_delete',
        view=TagDeleteActionView.as_view()
    ),
    url(
        regex=r'^tags/multiple/remove/document/(?P<document_pk>\d+)/$',
        name='single_document_multiple_tag_remove',
        view=TagRemoveActionView.as_view()
    ),
    url(
        regex=r'^tags/multiple/remove/document/multiple/$',
        name='multiple_documents_selection_tag_remove',
        view=TagRemoveActionView.as_view()
    ),

    url(
        regex=r'^documents/(?P<document_pk>\d+)/attach/$',
        name='tag_attach', view=TagAttachActionView.as_view()
    ),
    url(
        regex=r'^documents/multiple/attach//$',
        name='multiple_documents_tag_attach',
        view=TagAttachActionView.as_view()
    ),

    url(
        regex=r'^documents/(?P<document_pk>\d+)/tags/$', name='document_tags',
        view=DocumentTagListView.as_view(),
    ),
]

api_urls = [
    url(
        regex=r'^tags/(?P<tag_pk>\d+)/documents/$',
        name='tag-document-list', view=APITagDocumentListView.as_view(),
    ),
    url(
        regex=r'^tags/(?P<tag_pk>\d+)/$', name='tag-detail',
        view=APITagView.as_view()
    ),
    url(regex=r'^tags/$', name='tag-list', view=APITagListView.as_view()),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/tags/$',
        name='document-tag-list', view=APIDocumentTagListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/tags/(?P<tag_pk>[0-9]+)/$',
        name='document-tag-detail', view=APIDocumentTagView.as_view()
    ),
]

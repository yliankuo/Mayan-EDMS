from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APICommentListView, APICommentView
from .views import (
    DocumentCommentCreateView, DocumentCommentDeleteView,
    DocumentCommentListView
)

urlpatterns = [
    url(
        regex=r'^comments/(?P<comment_pk>\d+)/delete/$', name='comment_delete',
        view=DocumentCommentDeleteView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/comments/add/$',
        name='comment_add', view=DocumentCommentCreateView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/comments/$',
        name='comments_for_document', view=DocumentCommentListView.as_view()
    ),
]

api_urls = [
    url(
        regex=r'^documents/(?P<document_pk>[0-9]+)/comments/$',
        name='comment-list', view=APICommentListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>[0-9]+)/comments/(?P<comment_pk>[0-9]+)/$',
        name='comment-detail', view=APICommentView.as_view()
    ),
]

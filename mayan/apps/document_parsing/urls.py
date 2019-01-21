from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APIDocumentPageContentView
from .views import (
    DocumentContentDownloadView, DocumentContentView, DocumentPageContentView,
    DocumentParsingErrorsListView, DocumentSubmitView,
    DocumentTypeSettingsEditView, DocumentTypeSubmitView, ParseErrorListView
)

urlpatterns = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/content/$',
        name='document_content', view=DocumentContentView.as_view()
    ),
    url(
        regex=r'^documents/pages/(?P<document_page_id>\d+)/content/$',
        name='document_page_content', view=DocumentPageContentView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/content/download/$',
        name='document_content_download',
        view=DocumentContentDownloadView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/submit/$',
        name='document_submit', view=DocumentSubmitView.as_view()
    ),
    url(
        regex=r'^documents/multiple/submit/$', name='document_multiple_submit',
        view=DocumentSubmitView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/errors/$',
        name='document_parsing_error_list',
        view=DocumentParsingErrorsListView.as_view()
    ),
    url(
        regex=r'^document_types/submit/$', name='document_type_submit',
        view=DocumentTypeSubmitView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_id>\d+)/parsing/settings/$',
        name='document_type_parsing_settings',
        view=DocumentTypeSettingsEditView.as_view()
    ),
    url(
        regex=r'^errors/all/$', name='error_list',
        view=ParseErrorListView.as_view()
    )
]

api_urls = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/versions/(?P<document_version_id>\d+)/pages/(?P<document_page_id>\d+)/content/$',
        view=APIDocumentPageContentView.as_view(),
        name='document-page-content-view'
    )
]

from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APICheckedoutDocumentListView, APICheckedoutDocumentView
from .views import (
    CheckoutDetailView, CheckoutDocumentView, CheckoutListView,
    DocumentCheckinView
)

urlpatterns = [
    url(
        regex=r'^documents/$', name='checkout_list',
        view=CheckoutListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/check/out/$',
        name='checkout_document', view=CheckoutDocumentView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/check/in/$',
        name='checkin_document', view=DocumentCheckinView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/check/info/$',
        name='checkout_info', view=CheckoutDetailView.as_view()
    ),
]

api_urls = [
    url(
        regex=r'^checkouts/$', name='checkout-document-list',
        view=APICheckedoutDocumentListView.as_view()
    ),
    url(
        regex=r'^checkouts/(?P<document_pk>[0-9]+)/checkout_info/$',
        name='checkedout-document-view',
        view=APICheckedoutDocumentView.as_view()
    ),
]

from __future__ import unicode_literals

from django.conf.urls import url

from .views import (
    TransformationCreateView, TransformationDeleteView, TransformationEditView,
    TransformationListView
)

urlpatterns = [
    url(
        regex=r'^create_for/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/$',
        name='transformation_create', view=TransformationCreateView.as_view()
    ),
    url(
        regex=r'^list_for/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/$',
        name='transformation_list', view=TransformationListView.as_view()
    ),
    url(
        regex=r'^delete/(?P<transformation_pk>\d+)/$',
        name='transformation_delete', view=TransformationDeleteView.as_view()
    ),
    url(
        regex=r'^edit/(?P<transformation_pk>\d+)/$',
        name='transformation_edit', view=TransformationEditView.as_view()
    ),
]

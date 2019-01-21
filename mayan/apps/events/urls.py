from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIEventListView, APIEventTypeListView, APIEventTypeNamespaceDetailView,
    APIEventTypeNamespaceEventTypeListView, APIEventTypeNamespaceListView,
    APINotificationListView, APIObjectEventListView
)
from .views import (
    CurrentUserEventListView, EventListView, EventTypeSubscriptionListView,
    NotificationListView, NotificationMarkRead, NotificationMarkReadAll,
    ObjectEventListView, ObjectEventTypeSubscriptionListView,
    VerbEventListView
)

urlpatterns = [
    url(regex=r'^events/$', name='events_list', view=EventListView.as_view()),
    url(
        regex=r'^events/by_verb/(?P<verb>[\w\-\.]+)/$', name='events_by_verb',
        view=VerbEventListView.as_view()
    ),
    url(
        regex=r'^objects/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/events/$',
        name='events_for_object', view=ObjectEventListView.as_view()
    ),
    url(
        regex=r'^user/events/$', name='current_user_events',
        view=CurrentUserEventListView.as_view()
    ),
    url(
        regex=r'^user/event_types/subscriptions/$',
        name='event_types_user_subcriptions_list',
        view=EventTypeSubscriptionListView.as_view()
    ),
    url(
        regex=r'^user/notifications/$', name='user_notifications_list',
        view=NotificationListView.as_view()
    ),
    url(
        regex=r'^user/notifications/(?P<notification_id>\d+)/mark_read/$',
        name='notification_mark_read', view=NotificationMarkRead.as_view()
    ),
    url(
        regex=r'^user/notifications/all/mark_read/$',
        name='notification_mark_read_all',
        view=NotificationMarkReadAll.as_view()
    ),
    url(
        regex=r'^user/subscriptions/for/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/$',
        name='object_event_types_user_subcriptions_list',
        view=ObjectEventTypeSubscriptionListView.as_view()
    )
]

api_urls = [
    url(
        regex=r'^event_type_namespaces/(?P<name>[-\w]+)/$',
        name='event-type-namespace-detail',
        view=APIEventTypeNamespaceDetailView.as_view()
    ),
    url(
        regex=r'^event_type_namespaces/(?P<name>[-\w]+)/event_types/$',
        name='event-type-namespace-event-type-list',
        view=APIEventTypeNamespaceEventTypeListView.as_view()
    ),
    url(
        regex=r'^event_type_namespaces/$', name='event-type-namespace-list',
        view=APIEventTypeNamespaceListView.as_view()
    ),
    url(
        regex=r'^event_types/$', name='event-type-list',
        view=APIEventTypeListView.as_view()
    ),
    url(regex=r'^events/$', name='event-list', view=APIEventListView.as_view()),
    url(
        regex=r'^notifications/$', name='notification-list',
        view=APINotificationListView.as_view()
    ),
    url(
        regex=r'^objects/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/events/$',
        name='object-event-list', view=APIObjectEventListView.as_view()
    )
]

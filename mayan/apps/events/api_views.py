from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from actstream.models import Action, any_stream
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from mayan.apps.acls.models import AccessControlList

from .classes import EventType, EventTypeNamespace
from .models import Notification
from .permissions import permission_events_view
from .serializers import (
    EventSerializer, EventTypeNamespaceSerializer, EventTypeSerializer,
    NotificationSerializer
)



class EventTypeNamespaceAPIViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'name'
    lookup_url_kwarg = 'event_type_namespace_name'
    serializer_class = EventTypeNamespaceSerializer

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        return EventTypeNamespace.get(**filter_kwargs)

    @action(
        detail=True, serializer_class=EventTypeSerializer,
        url_name='event_type-list', url_path='event_types'
    )
    def event_type_list(self, request, *args, **kwargs):
        queryset = self.get_object().event_types
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    def get_queryset(self):
        return EventTypeNamespace.all()


class EventTypeAPIViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'id'
    lookup_url_kwarg = 'event_type_id'
    lookup_value_regex = r'[\w\.]+'
    serializer_class = EventTypeSerializer

    def get_object(self):
        namespace = EventTypeNamespace.get(name=self.kwargs['event_type_namespace_name'])
        event_types = namespace.get_event_types()
        return event_types.get(self.kwargs['event_type_id'])



'''
class APIObjectEventListView(generics.ListAPIView):
    """
    get: Return a list of events for the specified object.
    """
    serializer_class = EventSerializer

    def get_object(self):
        content_type = get_object_or_404(
            klass=ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        try:
            return content_type.get_object_for_this_type(
                pk=self.kwargs['object_id']
            )
        except content_type.model_class().DoesNotExist:
            raise Http404

    def get_queryset(self):
        obj = self.get_object()

        AccessControlList.objects.check_access(
            permissions=permission_events_view, user=self.request.user,
            obj=obj
        )

        return any_stream(obj)


class APINotificationListView(generics.ListAPIView):
    """
    get: Return a list of notifications for the current user.
    """
    serializer_class = NotificationSerializer

    def get_queryset(self):
        parameter_read = self.request.GET.get('read')

        if self.request.user.is_authenticated:
            queryset = Notification.objects.filter(user=self.request.user)
        else:
            queryset = Notification.objects.none()

        if parameter_read == 'True':
            queryset = queryset.filter(read=True)
        elif parameter_read == 'False':
            queryset = queryset.filter(read=False)

        return queryset
'''

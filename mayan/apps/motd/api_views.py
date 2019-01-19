from __future__ import absolute_import, unicode_literals

from rest_framework import viewsets

from mayan.apps.rest_api.filters import MayanObjectPermissionsFilter
from mayan.apps.rest_api.permissions import MayanPermission

from .models import Message
from .permissions import (
    permission_message_create, permission_message_delete,
    permission_message_edit, permission_message_view
)
from .serializers import MessageSerializer


class APIMessageViewSet(viewsets.ModelViewSet):
    """
    create:
    Create a new message.

    delete:
    Delete the given message.

    edit:
    Edit the given message.

    list:
    Return a list of all the messages.

    retrieve:
    Return the given message details.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    lookup_url_kwarg = 'message_id'
    object_permission = {
        'DELETE': permission_message_delete,
        'GET': permission_message_view,
        'PATCH': permission_message_edit,
        'PUT': permission_message_edit,
    }
    queryset = Message.objects.all()
    permission_classes = (MayanPermission,)
    serializer_class = MessageSerializer
    view_permission = {
        'POST': permission_message_create
    }

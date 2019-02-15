from __future__ import absolute_import, unicode_literals

from rest_framework import viewsets
from rest_framework.settings import api_settings

from .filters import MayanViewSetObjectPermissionsFilter
from .permissions import MayanViewSetPermission


class MayanAPIGenericViewSet(viewsets.GenericViewSet):
    filter_backends = (MayanViewSetObjectPermissionsFilter,)
    permission_classes = (MayanViewSetPermission,)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class MayanAPIModelViewSet(viewsets.ModelViewSet):
    filter_backends = (MayanViewSetObjectPermissionsFilter,)
    permission_classes = (MayanViewSetPermission,)

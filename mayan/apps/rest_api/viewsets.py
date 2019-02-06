from __future__ import absolute_import, unicode_literals

from rest_framework import viewsets

from .filters import MayanViewSetObjectPermissionsFilter
from .permissions import MayanViewSetPermission


class MayanAPIModelViewSet(viewsets.ModelViewSet):
    filter_backends = (MayanViewSetObjectPermissionsFilter,)
    permission_classes = (MayanViewSetPermission,)

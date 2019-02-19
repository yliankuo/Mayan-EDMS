from __future__ import absolute_import, unicode_literals

from rest_framework import viewsets
from rest_framework.settings import api_settings

from .filters import MayanViewSetObjectPermissionsFilter
from .mixins import SuccessHeadersMixin
from .permissions import MayanViewSetPermission


class MayanAPIGenericViewSet(SuccessHeadersMixin, viewsets.GenericViewSet):
    filter_backends = (MayanViewSetObjectPermissionsFilter,)
    permission_classes = (MayanViewSetPermission,)


class MayanAPIModelViewSet(SuccessHeadersMixin, viewsets.ModelViewSet):
    filter_backends = (MayanViewSetObjectPermissionsFilter,)
    permission_classes = (MayanViewSetPermission,)


class MayanAPIReadOnlyModelViewSet(SuccessHeadersMixin, viewsets.ReadOnlyModelViewSet):
    filter_backends = (MayanViewSetObjectPermissionsFilter,)
    permission_classes = (MayanViewSetPermission,)


class MayanAPIViewSet(SuccessHeadersMixin, viewsets.GenericViewSet):
    filter_backends = (MayanViewSetObjectPermissionsFilter,)
    permission_classes = (MayanViewSetPermission,)

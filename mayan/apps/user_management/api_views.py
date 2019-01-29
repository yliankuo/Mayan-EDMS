from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

from rest_framework import generics

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.rest_api.filters import MayanObjectPermissionsFilter
from mayan.apps.rest_api.permissions import MayanPermission

from .permissions import (
    permission_group_create, permission_group_delete, permission_group_edit,
    permission_group_view, permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)
from .serializers import (
    GroupSerializer, UserSerializer#, UserGroupListSerializer
)


class APICurrentUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the current user.
    get: Return the details of the current user.
    patch: Partially edit the current user.
    put: Edit the current user.
    """
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class APIGroupListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the groups.
    post: Create a new group.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_group_view,)}
    mayan_view_permissions = {'POST': (permission_group_create,)}
    permission_classes = (MayanPermission,)
    queryset = Group.objects.order_by('id')
    serializer_class = GroupSerializer


class APIGroupView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected group.
    get: Return the details of the selected group.
    patch: Partially edit the selected group.
    put: Edit the selected group.
    """
    lookup_url_kwarg = 'group_pk'
    mayan_object_permissions = {
        'GET': (permission_group_view,),
        'PUT': (permission_group_edit,),
        'PATCH': (permission_group_edit,),
        'DELETE': (permission_group_delete,)
    }
    permission_classes = (MayanPermission,)
    queryset = Group.objects.order_by('id')
    serializer_class = GroupSerializer


class APIUserListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the users.
    post: Create a new user.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_user_view,)}
    mayan_view_permissions = {'POST': (permission_user_create,)}
    permission_classes = (MayanPermission,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class APIUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected user.
    get: Return the details of the selected user.
    patch: Partially edit the selected user.
    put: Edit the selected user.
    """
    lookup_url_kwarg = 'user_pk'
    mayan_object_permissions = {
        'GET': (permission_user_view,),
        'PUT': (permission_user_edit,),
        'PATCH': (permission_user_edit,),
        'DELETE': (permission_user_delete,)
    }
    permission_classes = (MayanPermission,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class APIUserGroupList(ExternalObjectMixin, generics.ListCreateAPIView):
    """
    get: Returns a list of all the groups to which an user belongs.
    post: Add a user to a list of groups.
    """
    external_object_pk_url_kwarg = 'user_pk'
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_group_view,),
        'POST': (permission_group_edit,)
    }

    def get_external_object_permission(self):
        if self.request.method == 'POST':
            return permission_user_edit
        else:
            return permission_user_view

    def get_external_object_queryset(self):
        return get_user_model().objects.exclude(is_staff=True).exclude(
            is_superuser=True
        )

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APIUserGroupList, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserSerializer
        else:
            return GroupSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIUserGroupList, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'user': self.get_user(),
                }
            )

        return context

    def get_queryset(self):
        return self.get_user().groups.order_by('id')

    def get_user(self):
        return self.get_external_object()

    def perform_create(self, serializer):
        return serializer.save(user=self.get_object(), _user=self.request.user)

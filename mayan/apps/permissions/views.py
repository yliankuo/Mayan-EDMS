from __future__ import unicode_literals

import itertools

from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    AssignRemoveView, SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectEditView, SingleObjectListView
)
from mayan.apps.user_management.permissions import permission_group_edit

from .classes import Permission, PermissionNamespace
from .icons import icon_role_list
from .links import link_role_create
from .models import Role, StoredPermission
from .permissions import (
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)


class GroupRolesView(AssignRemoveView):
    grouped = False
    left_list_title = _('Available roles')
    right_list_title = _('Group roles')
    object_permission = permission_group_edit

    def add(self, item):
        role = get_object_or_404(klass=Role, pk=item)
        self.get_object().roles.add(role)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Roles of group: %s') % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(klass=Group, pk=self.kwargs['group_id'])

    def left_list(self):
        return [
            (force_text(role.pk), role.label) for role in set(Role.objects.all()) - set(self.get_object().roles.all())
        ]

    def right_list(self):
        return [
            (force_text(role.pk), role.label) for role in self.get_object().roles.all()
        ]

    def remove(self, item):
        role = get_object_or_404(klass=Role, pk=item)
        self.get_object().roles.remove(role)


class RoleCreateView(SingleObjectCreateView):
    fields = ('label',)
    model = Role
    view_permission = permission_role_create
    post_action_redirect = reverse_lazy(viewname='permissions:role_list')


class RoleDeleteView(SingleObjectDeleteView):
    model = Role
    object_permission = permission_role_delete
    pk_url_kwarg = 'role_id'
    post_action_redirect = reverse_lazy(viewname='permissions:role_list')


class RoleEditView(SingleObjectEditView):
    fields = ('label',)
    model = Role
    object_permission = permission_role_edit
    pk_url_kwarg = 'role_id'


class RoleGroupsView(AssignRemoveView):
    grouped = False
    left_list_title = _('Available groups')
    right_list_title = _('Role groups')
    object_permission = permission_role_edit

    def add(self, item):
        group = get_object_or_404(klass=Group, pk=item)
        self.get_object().groups.add(group)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Groups of role: %s') % self.get_object(),
            'subtitle': _(
                'Add groups to be part of a role. They will '
                'inherit the role\'s permissions and access controls.'
            ),
        }

    def get_object(self):
        return get_object_or_404(klass=Role, pk=self.kwargs['role_id'])

    def left_list(self):
        return [
            (force_text(group.pk), group.name) for group in set(Group.objects.all()) - set(self.get_object().groups.all())
        ]

    def remove(self, item):
        group = get_object_or_404(klass=Group, pk=item)
        self.get_object().groups.remove(group)

    def right_list(self):
        return [
            (force_text(group.pk), group.name) for group in self.get_object().groups.all()
        ]


class RoleListView(SingleObjectListView):
    model = Role
    object_permission = permission_role_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_role_list,
            'no_results_main_link': link_role_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Roles are authorization units. They contain '
                'user groups which inherit the role permissions for the '
                'entire system. Roles can also part of access '
                'controls lists. Access controls list are permissions '
                'granted to a role for specific objects which its group '
                'members inherit.'
            ),
            'no_results_title': _('There are no roles'),
            'title': _('Roles'),
        }


class RolePermissionsView(AssignRemoveView):
    grouped = True
    left_list_title = _('Available permissions')
    object_permission = permission_role_edit
    right_list_title = _('Granted permissions')

    @staticmethod
    def generate_choices(entries):
        results = []

        entries = sorted(
            entries, key=lambda x: (
                x.volatile_permission.namespace.label,
                x.volatile_permission.label
            )
        )

        for namespace, permissions in itertools.groupby(entries, lambda entry: entry.namespace):
            permission_options = [
                (force_text(permission.pk), permission) for permission in permissions
            ]
            results.append(
                (PermissionNamespace.get(name=namespace), permission_options)
            )

        return results

    def add(self, item):
        permission = get_object_or_404(klass=StoredPermission, pk=item)
        self.get_object().permissions.add(permission)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'subtitle': _(
                'Permissions granted here will apply to the entire system '
                'and all objects.'
            ),
            'title': _('Permissions for role: %s') % self.get_object(),
        }

    def get_object(self):
        return get_object_or_404(klass=Role, pk=self.kwargs['role_id'])

    def left_list(self):
        Permission.refresh()

        return RolePermissionsView.generate_choices(
            entries=StoredPermission.objects.exclude(
                id__in=self.get_object().permissions.values_list('pk', flat=True)
            )
        )

    def remove(self, item):
        permission = get_object_or_404(klass=StoredPermission, pk=item)
        self.get_object().permissions.remove(permission)

    def right_list(self):
        return RolePermissionsView.generate_choices(
            entries=self.get_object().permissions.all()
        )

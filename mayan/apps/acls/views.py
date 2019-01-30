from __future__ import absolute_import, unicode_literals

import itertools
import logging

from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.mixins import (
    ContentTypeViewMixin, ExternalObjectMixin
)
from mayan.apps.common.generics import (
    AssignRemoveView, SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectListView
)
from mayan.apps.permissions import Permission, PermissionNamespace
from mayan.apps.permissions.models import Role, StoredPermission

from .classes import ModelPermission
from .forms import ACLCreateForm
from .icons import icon_acl_list
from .links import link_acl_create
from .models import AccessControlList
from .permissions import permission_acl_edit, permission_acl_view

logger = logging.getLogger(__name__)


class ACLCreateView(ContentTypeViewMixin, ExternalObjectMixin, SingleObjectCreateView):
    external_object_permission = permission_acl_edit
    external_object_pk_url_kwarg = 'object_id'
    form_class = ACLCreateForm

    def get_error_message_duplicate(self):
        return _(
            'An ACL for "%(object)s" using role "%(role)s" already exists. '
            'Edit that ACL entry instead.'
        ) % {'object': self.get_external_object(), 'role': self.object.role}

    def get_external_object_queryset(self):
        # Here we get a queryset the object model for which an ACL will be
        # created.
        return self.get_content_type().model_class().objects.all()

    def get_extra_context(self):
        return {
            'object': self.get_external_object(),
            'title': _(
                'New access control lists for: %s'
            ) % self.get_external_object()
        }

    def get_form_extra_kwargs(self):
        return {
            'field_name': 'role',
            'label': _('Role'),
            'queryset': Role.objects.exclude(
                pk__in=self.get_external_object().acls.values('role')
            ),
            'widget_attributes': {'class': 'select2'}
        }

    def get_instance_extra_data(self):
        return {
            'content_object': self.get_external_object()
        }

    def get_queryset(self):
        self.get_external_object().acls.all()

    def get_success_url(self):
        return self.object.get_absolute_url()


class ACLDeleteView(SingleObjectDeleteView):
    model = AccessControlList
    object_permission = permission_acl_edit
    pk_url_kwarg = 'acl_id'

    def get_extra_context(self):
        return {
            'object': self.get_object().content_object,
            'title': _('Delete ACL: %s') % self.get_object(),
        }

    def get_post_action_redirect(self):
        instance = self.get_object()
        return reverse(
            'acls:acl_list', kwargs={
                'app_label': instance.content_type.app_label,
                'model': instance.content_type.model,
                'object_id': instance.object_id
            }
        )


class ACLListView(ContentTypeViewMixin, ExternalObjectMixin, SingleObjectListView):
    external_object_permission = permission_acl_view
    external_object_pk_url_kwarg = 'object_id'

    def get_external_object_queryset(self):
        # Here we get a queryset the object model for which an ACL will be
        # created.
        return self.get_content_type().model_class().objects.all()

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_acl_list,
            'no_results_main_link': link_acl_create.resolve(
                context=RequestContext(
                    self.request, {
                        'resolved_object': self.get_external_object()
                    }
                )
            ),
            'no_results_title': _(
                'There are no ACLs for this object'
            ),
            'no_results_text': _(
                'ACL stands for Access Control List and is a precise method '
                ' to control user access to objects in the system. ACLs '
                'allow granting a permission to a role but only for a '
                'specific object or set of objects.'
            ),
            'object': self.get_external_object(),
            'title': _(
                'Access control lists for: %s' % self.get_external_object()
            ),
        }

    def get_source_queryset(self):
        return self.get_external_object().acls.all()


class ACLPermissionsView(AssignRemoveView):
    grouped = True
    left_list_title = _('Available permissions')
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

    def get_available_list(self):
        return ModelPermission.get_for_instance(
            instance=self.get_object().content_object
        ).exclude(id__in=self.get_granted_list().values_list('pk', flat=True))

    def get_disabled_choices(self):
        """
        Get permissions from a parent's acls but remove the permissions we
        already hold for this object
        """
        return map(
            str, set(
                self.get_object().get_inherited_permissions().values_list(
                    'pk', flat=True
                )
            ).difference(
                self.get_object().permissions.values_list('pk', flat=True)
            )
        )

    def get_extra_context(self):
        return {
            'object': self.get_object().content_object,
            'title': _('Role "%(role)s" permission\'s for "%(object)s"') % {
                'role': self.get_object().role,
                'object': self.get_object().content_object,
            },
        }

    def get_granted_list(self):
        """
        Merge of permissions we hold for this object and the permissions we
        hold for this object's parent via another ACL.
        """
        merged_pks = self.get_object().permissions.values_list(
            'pk', flat=True
        ) | self.get_object().get_inherited_permissions().values_list(
            'pk', flat=True
        )
        return StoredPermission.objects.filter(pk__in=merged_pks)

    def get_object(self):
        return get_object_or_404(
            klass=self.get_queryset(), pk=self.kwargs['acl_id']
        )

    def get_queryset(self):
        return AccessControlList.objects.restrict_queryset(
            permission=permission_acl_edit,
            queryset=AccessControlList.objects.all(), user=self.request.user
        )

    def get_right_list_help_text(self):
        if self.get_object().get_inherited_permissions():
            return _(
                'Disabled permissions are inherited from a parent object and '
                'can\'t be removed from this view, they need to be removed '
                'from the parent object\'s ACL view.'
            )

        return self.right_list_help_text

    def left_list(self):
        Permission.refresh()
        return ACLPermissionsView.generate_choices(self.get_available_list())

    def remove(self, item):
        permission = get_object_or_404(klass=StoredPermission, pk=item)
        self.get_object().permissions.remove(permission)

    def right_list(self):
        return ACLPermissionsView.generate_choices(self.get_granted_list())

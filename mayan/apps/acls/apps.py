from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.common import MayanAppConfig, menu_object, menu_sidebar
from mayan.apps.navigation import SourceColumn

from .classes import ModelPermission
from .links import link_acl_create, link_acl_delete, link_acl_permissions


class ACLsApp(MayanAppConfig):
    app_namespace = 'acls'
    app_url = 'acls'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.acls'
    verbose_name = _('ACLs')

    def ready(self):
        super(ACLsApp, self).ready()

        AccessControlList = self.get_model(model_name='AccessControlList')

        ModelPermission.register_inheritance(
            model=AccessControlList, related='content_object',
        )
        SourceColumn(
            attribute='role', is_identifier=True, is_sortable=True,
            source=AccessControlList
        )
        SourceColumn(
            attribute='get_permission_titles', include_label=True,
            source=AccessControlList
        )

        menu_object.bind_links(
            links=(link_acl_permissions, link_acl_delete),
            sources=(AccessControlList,)
        )
        menu_sidebar.bind_links(
            links=(link_acl_create,), sources=('acls:acl_list',)
        )

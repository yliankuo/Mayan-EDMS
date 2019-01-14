from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied

from mayan.apps.common.tests import BaseTestCase

from ..classes import Permission
from ..permissions import permission_role_view


class PermissionTestCase(BaseTestCase):
    def setUp(self):
        super(PermissionTestCase, self).setUp()

    def test_no_permissions(self):
        with self.assertRaises(PermissionDenied):
            Permission.check_user_permission(
                permission=permission_role_view, user=self._test_case_user
            )

    def test_with_permissions(self):
        self._test_case_group.user_set.add(self._test_case_user)
        self._test_case_role.permissions.add(permission_role_view.stored_permission)
        self._test_case_role.groups.add(self._test_case_group)

        try:
            Permission.check_user_permission(
                permission=permission_role_view, user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

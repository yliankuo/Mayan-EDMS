from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from mayan.apps.permissions.tests.mixins import RoleTestCaseMixin
from mayan.apps.user_management.tests.mixins import UserTestCaseMixin

from ..models import AccessControlList


class ACLTestCaseMixin(RoleTestCaseMixin, UserTestCaseMixin):

    def setUp(self):
        super(ACLTestCaseMixin, self).setUp()
        if hasattr(self, '_test_case_user'):
            self._test_case_role.groups.add(self._test_case_group)

    def grant_access(self, obj, permission):
        if not hasattr(self, '_test_case_role'):
            raise ImproperlyConfigured(
                'Enable the creation of the test case user, group, and role '
                'in order to enable the usage of ACLs in tests.'
            )

        return AccessControlList.objects.grant(
            obj=obj, permission=permission, role=self._test_case_role
        )

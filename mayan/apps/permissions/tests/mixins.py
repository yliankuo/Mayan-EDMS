from __future__ import unicode_literals

from ..models import Role

from .literals import TEST_CASE_ROLE_LABEL, TEST_ROLE_LABEL


class RoleTestCaseMixin(object):
    def setUp(self):
        super(RoleTestCaseMixin, self).setUp()
        if hasattr(self, '_test_case_group'):
            self.create_role()

    def create_role(self):
        self._test_case_role = Role.objects.create(label=TEST_CASE_ROLE_LABEL)

    def grant_permission(self, permission):
        self._test_case_role.grant(permission=permission)


class RoleTestMixin(object):
    def _create_test_role(self):
        self.test_role = Role.objects.create(label=TEST_ROLE_LABEL)

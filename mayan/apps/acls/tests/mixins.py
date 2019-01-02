from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from mayan.apps.permissions.models import Role
from mayan.apps.permissions.tests.literals import TEST_ROLE_LABEL
from mayan.apps.user_management.tests import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME,
    TEST_GROUP_NAME, TEST_USER_EMAIL, TEST_USER_PASSWORD,
    TEST_USER_USERNAME
)

from ..models import AccessControlList


class ACLBaseTestMixin(object):
    auto_create_group = True
    auto_create_users = True

    def setUp(self):
        super(ACLBaseTestMixin, self).setUp()
        if self.auto_create_users:
            self.admin_user = get_user_model().objects.create_superuser(
                username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
                password=TEST_ADMIN_PASSWORD
            )

            self.user = get_user_model().objects.create_user(
                username=TEST_USER_USERNAME, email=TEST_USER_EMAIL,
                password=TEST_USER_PASSWORD
            )

        if self.auto_create_group:
            self.group = Group.objects.create(name=TEST_GROUP_NAME)
            self.role = Role.objects.create(label=TEST_ROLE_LABEL)
            self.group.user_set.add(self.user)
            self.role.groups.add(self.group)

    def grant_access(self, obj, permission):
        return AccessControlList.objects.grant(
            obj=obj, permission=permission, role=self.role
        )

    def grant_permission(self, permission):
        self.role.permissions.add(
            permission.stored_permission
        )

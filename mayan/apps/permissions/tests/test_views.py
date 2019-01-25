from __future__ import unicode_literals

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.user_management.permissions import permission_group_edit
from mayan.apps.user_management.tests import GroupTestMixin

from ..models import Role
from ..permissions import (
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)

from .literals import TEST_ROLE_LABEL, TEST_ROLE_LABEL_EDITED
from .mixins import RoleTestMixin


class PermissionsViewsTestCase(GroupTestMixin, RoleTestMixin, GenericViewTestCase):
    def setUp(self):
        super(PermissionsViewsTestCase, self).setUp()
        self.login_user()

    def _request_create_role_view(self):
        return self.post(
            viewname='permissions:role_create', data={
                'label': TEST_ROLE_LABEL,
            }
        )

    def test_role_creation_view_no_permission(self):
        response = self._request_create_role_view()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Role.objects.count(), 1)
        self.assertFalse(
            TEST_ROLE_LABEL in Role.objects.values_list('label', flat=True)
        )

    def test_role_creation_view_with_permission(self):
        self.grant_permission(permission=permission_role_create)
        response = self._request_create_role_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Role.objects.count(), 2)
        self.assertTrue(
            TEST_ROLE_LABEL in Role.objects.values_list('label', flat=True)
        )

    def _request_role_delete_view(self):
        return self.post(
            viewname='permissions:role_delete',
            kwargs={'role_id': self.test_role.pk}
        )

    def test_role_delete_view_no_access(self):
        self._create_test_role()
        response = self._request_role_delete_view()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Role.objects.count(), 2)
        self.assertTrue(
            TEST_ROLE_LABEL in Role.objects.values_list('label', flat=True)
        )

    def test_role_delete_view_with_access(self):
        self._create_test_role()
        self.grant_access(permission=permission_role_delete, obj=self.test_role)
        response = self._request_role_delete_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Role.objects.count(), 1)
        self.assertFalse(
            TEST_ROLE_LABEL in Role.objects.values_list('label', flat=True)
        )

    def _request_role_edit_view(self):
        return self.post(
            viewname='permissions:role_edit',
            kwargs={'role_id': self.test_role.pk}, data={
                'label': TEST_ROLE_LABEL_EDITED,
            }
        )

    def test_role_edit_view_no_access(self):
        self._create_test_role()
        response = self._request_role_edit_view()

        self.assertEqual(response.status_code, 403)

        self.test_role.refresh_from_db()
        self.assertEqual(Role.objects.count(), 2)
        self.assertEqual(self.test_role.label, TEST_ROLE_LABEL)

    def test_role_edit_view_with_access(self):
        self._create_test_role()
        self.grant_access(permission=permission_role_edit, obj=self.test_role)
        response = self._request_role_edit_view()

        self.assertEqual(response.status_code, 302)
        self.test_role.refresh_from_db()

        self.assertEqual(Role.objects.count(), 2)
        self.assertEqual(self.test_role.label, TEST_ROLE_LABEL_EDITED)

    def _request_role_list_view(self):
        return self.get(viewname='permissions:role_list')

    def test_role_list_view_no_access(self):
        self._create_test_role()
        response = self._request_role_list_view()
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response=response, text=TEST_ROLE_LABEL, status_code=200
        )

    def test_role_list_view_with_access(self):
        self._create_test_role()
        self.grant_access(permission=permission_role_view, obj=self.test_role)
        response = self._request_role_list_view()
        self.assertContains(
            response=response, text=TEST_ROLE_LABEL, status_code=200
        )

    def _request_role_permissions_view(self):
        return self.get(
            viewname='permissions:role_permissions',
            kwargs={'role_id': self.test_role.pk}
        )

    def test_role_permissions_view_no_permission(self):
        self._create_test_role()
        response = self._request_role_permissions_view()
        self.assertEqual(response.status_code, 403)

    def test_role_permissions_view_with_access(self):
        self._create_test_role()
        self.grant_access(
            permission=permission_permission_view, obj=self.test_role
        )
        response = self._request_role_permissions_view()
        self.assertEqual(response.status_code, 200)

    def _request_role_groups_view(self):
        return self.get(
            viewname='permissions:role_groups',
            kwargs={'role_id': self.test_role.pk}
        )

    def test_role_groups_view_no_access(self):
        self._create_test_role()
        response = self._request_role_groups_view()
        self.assertEqual(response.status_code, 403)

    def test_role_groups_view_with_access(self):
        self._create_test_role()
        self.grant_access(permission=permission_role_edit, obj=self.test_role)
        response = self._request_role_groups_view()
        self.assertEqual(response.status_code, 200)

    def _request_group_roles_view(self):
        return self.get(
            viewname='permissions:group_roles',
            kwargs={'group_id': self.test_group.pk}
        )

    def test_group_roles_view_no_access(self):
        self._create_test_group()
        response = self._request_group_roles_view()
        self.assertEqual(response.status_code, 403)

    def test_group_roles_view_with_access(self):
        self._create_test_group()
        self.grant_access(permission=permission_group_edit, obj=self.test_group)
        response = self._request_group_roles_view()
        self.assertEqual(response.status_code, 200)

from __future__ import absolute_import, unicode_literals

from django.utils.encoding import force_text

from mayan.apps.documents.tests import GenericDocumentViewTestCase
from mayan.apps.permissions.tests.mixins import RoleTestMixin

from ..models import AccessControlList
from ..permissions import permission_acl_edit, permission_acl_view

from .mixins import ACLTestMixin


class AccessControlListViewTestCase(ACLTestMixin, RoleTestMixin, GenericDocumentViewTestCase):
    def _request_acl_create_get_view(self):
        return self.get(
            viewname='acls:acl_create',
            kwargs=self.test_content_object_view_kwargs, data={
                'role': self.test_role.pk
            }
        )

    def test_acl_create_get_view_no_permission(self):
        response = self._request_acl_create_get_view()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(AccessControlList.objects.count(), 0)

    def test_acl_create_get_view_with_document_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        response = self._request_acl_create_get_view()
        self.assertContains(
            response=response, text=force_text(self.test_object),
            status_code=200
        )

    def _request_acl_create_post_view(self):
        return self.post(
            viewname='acls:acl_create',
            kwargs=self.test_content_object_view_kwargs, data={
                'role': self.test_role.pk
            }
        )

    def test_acl_create_view_post_no_permission(self):
        response = self._request_acl_create_post_view()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(AccessControlList.objects.count(), 0)

    def test_acl_create_view_post_with_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        response = self._request_acl_create_post_view()
        self.assertEqual(response.status_code, 302)

        # 2 ACLs: 1 created by the test and the other by the self.grant_access
        self.assertEqual(AccessControlList.objects.count(), 2)

    def test_acl_create_duplicate_view_with_access(self):
        """
        Test creating a duplicate ACL entry: same object & role
        Result: Should redirect to existing ACL for object + role combination
        """
        self._create_test_acl()

        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        response = self._request_acl_create_post_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_acl.role),
            status_code=200
        )

        # 2 ACLs: 1 created by the test and the other by the self.grant_access
        self.assertEqual(AccessControlList.objects.count(), 2)

        # Sorted by role PK
        expected_results = sorted(
            [
                {
                    # Test role, created and then requested,
                    # but created only once
                    'object_id': self.test_object.pk,
                    'role': self.test_role.pk
                },
                {
                    # Test case ACL for the test case role, ignored
                    'object_id': self.test_object.pk,
                    'role': self._test_case_role.pk
                },
            ], key=lambda item: item['role']
        )

        self.assertQuerysetEqual(
            qs=AccessControlList.objects.order_by('role__id').values(
                'object_id', 'role',
            ), transform=dict, values=expected_results
        )

    def _request_acl_delete_view(self):
        return self.post(
            viewname='acls:acl_delete', kwargs={'acl_id': self.test_acl.pk}
        )

    def test_acl_delete_view_no_permission(self):
        self._create_test_acl()

        response = self._request_acl_delete_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_object),
            status_code=404
        )

        # 1 ACL: the test one
        self.assertQuerysetEqual(
            qs=AccessControlList.objects.all(), values=(repr(self.test_acl),)
        )

    def test_acl_delete_view_with_access(self):
        self._create_test_acl()

        self.grant_access(
            obj=self.test_object, permission=permission_acl_edit
        )

        response = self._request_acl_delete_view()
        self.assertEqual(response.status_code, 302)

        # 1 ACL: the one created by the self.grant_access
        self.assertQuerysetEqual(
            qs=AccessControlList.objects.all(), values=(
                repr(self._test_case_acl),
            )
        )

    def _request_acl_list_view(self):
        return self.get(
            viewname='acls:acl_list', kwargs=self.test_content_object_view_kwargs
        )

    def test_acl_list_view_no_permission(self):
        response = self._request_acl_list_view()

        self.assertNotContains(
            response=response, text=force_text(self.test_object),
            status_code=404
        )

    def test_acl_list_view_with_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_view)

        response = self._request_acl_list_view()

        self.assertContains(
            response=response, text=force_text(self.test_object),
            status_code=200
        )

    def _request_get_acl_permissions_view(self):
        return self.get(
            viewname='acls:acl_permissions',
            kwargs={'acl_id': self.test_acl.pk}
        )

    def test_acl_permissions_view_get_no_permission(self):
        self._create_test_acl()

        response = self._request_get_acl_permissions_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_object),
            status_code=404
        )

    def test_acl_permissions_view_get_with_access(self):
        self._create_test_acl()

        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        response = self._request_get_acl_permissions_view()
        self.assertContains(
            response=response, text=force_text(self.test_object),
            status_code=200
        )

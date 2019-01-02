from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text

from mayan.apps.documents.tests import GenericDocumentViewTestCase
from mayan.apps.permissions.tests.mixins import RoleTestMixin

from ..models import AccessControlList
from ..permissions import permission_acl_edit, permission_acl_view


class AccessControlListViewTestCase(RoleTestMixin, GenericDocumentViewTestCase):
    def setUp(self):
        super(AccessControlListViewTestCase, self).setUp()
        self.login_user()
        self._create_test_role()

        self.test_object = self.document

        content_type = ContentType.objects.get_for_model(self.test_object)

        self.view_content_object_arguments = {
            'app_label': content_type.app_label,
            'model': content_type.model,
            'object_id': self.test_object.pk
        }

    def _request_get_acl_create_view(self):
        return self.get(
            viewname='acls:acl_create',
            kwargs=self.view_content_object_arguments, data={
                'role': self.test_role.pk
            }
        )

    def test_acl_create_view_get_no_permission(self):
        response = self._request_get_acl_create_view()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(AccessControlList.objects.count(), 0)

    def test_acl_create_view_get_with_document_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        response = self._request_get_acl_create_view()

        self.assertContains(
            response=response, text=force_text(self.test_object),
            status_code=200
        )

    def _request_post_acl_create_view(self):
        return self.post(
            viewname='acls:acl_create',
            kwargs=self.view_content_object_arguments, data={
                'role': self.test_role.pk
            }
        )

    def test_acl_create_view_post_no_permission(self):
        response = self._request_post_acl_create_view()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(AccessControlList.objects.count(), 0)

    def test_acl_create_view_post_with_document_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)
        response = self._request_post_acl_create_view()

        self.assertEqual(response.status_code, 302)
        # 2 ACLs: 1 created by the test and the other by the self.grant_access
        self.assertEqual(AccessControlList.objects.count(), 2)

    def test_acl_create_duplicate_view_with_permission(self):
        """
        Test creating a duplicate ACL entry: same object & role
        Result: Should redirect to existing ACL for object + role combination
        """
        self._create_test_acl()

        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        response = self._request_post_acl_create_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_acl.role),
            status_code=200
        )

        self.assertEqual(AccessControlList.objects.count(), 2)
        self.assertEqual(
            AccessControlList.objects.first().pk, self.test_acl.pk
        )

    def _create_test_acl(self):
        self.test_acl = AccessControlList.objects.create(
            content_object=self.test_object, role=self.test_role
        )

    def _request_acl_delete_view(self):
        return self.post(
            viewname='acls:acl_delete', kwargs={'acl_pk': self.test_acl.pk}
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

        acl = self.grant_access(
            obj=self.test_object, permission=permission_acl_edit
        )
        response = self._request_acl_delete_view()
        self.assertEqual(response.status_code, 302)
        # 1 ACL: the one created by the self.grant_access
        self.assertQuerysetEqual(
            qs=AccessControlList.objects.all(), values=(repr(acl),)
        )

    def _request_acl_list_view(self):
        return self.get(
            viewname='acls:acl_list', kwargs=self.view_content_object_arguments
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
            kwargs={'acl_pk': self.test_acl.pk}
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

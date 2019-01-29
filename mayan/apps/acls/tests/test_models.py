from __future__ import absolute_import, unicode_literals

from django.core.exceptions import PermissionDenied

from mayan.apps.common.tests import BaseTestCase
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests import (
    DocumentTestMixin, TEST_DOCUMENT_TYPE_2_LABEL, TEST_DOCUMENT_TYPE_LABEL
)

from ..models import AccessControlList


class PermissionTestCase(DocumentTestMixin, BaseTestCase):
    auto_create_document_type = False

    def setUp(self):
        super(PermissionTestCase, self).setUp()
        self.test_document_type_1 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        self.test_document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        self.test_document_1 = self.upload_document(
            document_type=self.test_document_type_1
        )
        self.test_document_2 = self.upload_document(
            document_type=self.test_document_type_1
        )
        self.test_document_3 = self.upload_document(
            document_type=self.test_document_type_2
        )

    def test_check_access_without_permissions(self):
        with self.assertRaises(PermissionDenied):
            AccessControlList.objects.check_access(
                obj=self.test_document_1, permission=permission_document_view,
                user=self._test_case_user
            )

    def test_filtering_without_permissions(self):
        self.assertEqual(
            AccessControlList.objects.restrict_queryset(
                permission=permission_document_view,
                queryset=Document.objects.all(), user=self._test_case_user,
            ).count(), 0
        )

    def test_check_access_with_acl(self):
        acl = AccessControlList.objects.create(
            content_object=self.test_document_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        try:
            AccessControlList.objects.check_access(
                obj=self.test_document_1, permission=permission_document_view,
                user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_filtering_with_permissions(self):
        acl = AccessControlList.objects.create(
            content_object=self.test_document_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        self.assertQuerysetEqual(
            AccessControlList.objects.restrict_queryset(
                permission=permission_document_view,
                queryset=Document.objects.all(), user=self._test_case_user
            ), (repr(self.test_document_1),)
        )

    def test_check_access_with_inherited_acl(self):
        acl = AccessControlList.objects.create(
            content_object=self.test_document_type_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        try:
            AccessControlList.objects.check_access(
                obj=self.test_document_1, permission=permission_document_view,
                user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_check_access_with_inherited_acl_and_direct_acl(self):
        test_acl_1 = AccessControlList.objects.create(
            content_object=self.test_document_type_1, role=self._test_case_role
        )
        test_acl_1.permissions.add(permission_document_view.stored_permission)

        test_acl_2 = AccessControlList.objects.create(
            content_object=self.test_document_3, role=self._test_case_role
        )
        test_acl_2.permissions.add(permission_document_view.stored_permission)

        try:
            AccessControlList.objects.check_access(
                obj=self.test_document_3, permission=permission_document_view,
                user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_filtering_with_inherited_permissions(self):
        acl = AccessControlList.objects.create(
            content_object=self.test_document_type_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        result = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view, queryset=Document.objects.all(),
            user=self._test_case_user
        )

        # Since document_1 and document_2 are of document_type_1
        # they are the only ones that should be returned

        self.assertTrue(self.test_document_1 in result)
        self.assertTrue(self.test_document_2 in result)
        self.assertTrue(self.test_document_3 not in result)

    def test_filtering_with_inherited_permissions_and_local_acl(self):
        self._test_case_role.permissions.add(
            permission_document_view.stored_permission
        )

        acl = AccessControlList.objects.create(
            content_object=self.test_document_type_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        acl = AccessControlList.objects.create(
            content_object=self.test_document_3, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        result = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view, queryset=Document.objects.all(),
            user=self._test_case_user,
        )
        self.assertTrue(self.test_document_1 in result)
        self.assertTrue(self.test_document_2 in result)
        self.assertTrue(self.test_document_3 in result)

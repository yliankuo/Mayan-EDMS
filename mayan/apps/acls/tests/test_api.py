from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType

from rest_framework import status

from mayan.apps.common.tests.mixins import TestModelTestMixin
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests import DocumentTestMixin
from mayan.apps.permissions.tests.literals import TEST_ROLE_LABEL
from mayan.apps.permissions.tests.mixins import PermissionTestMixin, RoleTestMixin
from mayan.apps.rest_api.tests import BaseAPITestCase

from ..classes import ModelPermission
from ..models import AccessControlList
from ..permissions import permission_acl_edit, permission_acl_view

from .mixins import ACLTestMixin


class ACLAPITestCase(ACLTestMixin, RoleTestMixin, PermissionTestMixin, TestModelTestMixin, BaseAPITestCase):
    def setUp(self):
        super(ACLAPITestCase, self).setUp()

        self._create_test_model()
        self._create_test_object()
        self._create_test_acl()
        ModelPermission.register(
            model=self.test_object._meta.model, permissions=(
                permission_acl_edit, permission_acl_view,
            )
        )

        self._create_test_permission()
        ModelPermission.register(
            model=self.test_object._meta.model, permissions=(
                self.test_permission,
            )
        )
        self.test_acl.permissions.add(self.test_permission.stored_permission)
        self._inject_test_object_content_type()

    def _request_object_acl_list_api_view(self):
        return self.get(
            viewname='rest_api:object-acl-list',
            kwargs=self.test_content_object_view_kwargs
        )

    def test_object_acl_list_api_view_no_permission(self):
        response = self._request_object_acl_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_object_acl_list_api_view_with_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_view)

        response = self._request_object_acl_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['content_type']['app_label'],
            self.test_object_content_type.app_label
        )
        self.assertEqual(
            response.data['results'][0]['role']['label'],
            self.test_acl.role.label
        )

    def _request_acl_delete_api_view(self):
        kwargs = self.test_content_object_view_kwargs.copy()
        kwargs['acl_id'] = self.test_acl.pk

        return self.delete(
            viewname='rest_api:object-acl-detail',
            kwargs=kwargs
        )

    def test_object_acl_delete_api_view_with_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)
        response = self._request_acl_delete_api_view()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(self.test_acl not in AccessControlList.objects.all())

    def test_object_acl_delete_api_view_no_permission(self):
        response = self._request_acl_delete_api_view()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_acl in AccessControlList.objects.all())

    def test_object_acl_detail_view(self):
        self._create_acl()

        response = self.get(
            viewname='rest_api:object-acl-detail',
            kwargs={
                'app_label': self.document_content_type.app_label,
                'model': self.document_content_type.model,
                'object_id': self.document.pk,
                'acl_pk': self.acl.pk
            }
        )
        self.assertEqual(
            response.data['content_type']['app_label'],
            self.document_content_type.app_label
        )
        self.assertEqual(
            response.data['role']['label'], TEST_ROLE_LABEL
        )

    def test_object_acl_permission_delete_view(self):
        self._create_acl()
        permission = self.acl.permissions.first()

        response = self.delete(
            viewname='rest_api:object-acl-permission-detail',
            kwargs={
                'app_label': self.document_content_type.app_label,
                'model_name': self.document_content_type.model,
                'object_id': self.document.pk,
                'acl_id': self.acl.pk, 'permission_id': permission.pk
            }
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.acl.permissions.count(), 0)

    def test_object_acl_permission_detail_view(self):
        self._create_acl()
        permission = self.acl.permissions.first()

        response = self.get(
            viewname='rest_api:object-acl-permission-detail',
            kwargs={
                'app_label': self.document_content_type.app_label,
                'model_name': self.document_content_type.model,
                'object_id': self.document.pk, 'acl_pk': self.acl.pk,
                'permission_pk': permission.pk
            }
        )

        self.assertEqual(
            response.data['permission_pk'], permission_document_view.pk
        )

    def test_object_acl_permission_list_view(self):
        self._create_acl()

        response = self.get(
            viewname='rest_api:object-acl-permission-list',
            kwargs={
                'app_label': self.document_content_type.app_label,
                'model_name': self.document_content_type.model,
                'object_id': self.document.pk,
                'acl_id': self.acl.pk
            }
        )

        self.assertEqual(
            response.data['results'][0]['permission_pk'],
            permission_document_view.pk
        )

    def test_object_acl_permission_list_post_view(self):
        self._create_acl()

        response = self.post(
            viewname='rest_api:object-acl-permission-list',
            kwargs={
                'app_label': self.document_content_type.app_label,
                'model_name': self.document_content_type.model,
                'object_id': self.document.pk, 'acl_pk': self.acl.pk
            }, data={'permission_id': permission_acl_view.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertQuerysetEqual(
            ordered=False, qs=self.acl.permissions.all(), values=(
                repr(permission_document_view.stored_permission),
                repr(permission_acl_view.stored_permission)
            )
        )

    def test_object_acl_post_no_permissions_added_view(self):
        response = self.post(
            viewname='rest_api:object-acl-list',
            kwargs={
                'app_label': self.document_content_type.app_label,
                'model_name': self.document_content_type.model,
                'object_id': self.document.pk
            }, data={'role_id': self.test_role.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            self.document.acls.first().role, self.test_role
        )
        self.assertEqual(
            self.document.acls.first().content_object, self.document
        )
        self.assertEqual(
            self.document.acls.first().permissions.count(), 0
        )

    def test_object_acl_post_with_permissions_added_view(self):
        response = self.post(
            viewname='rest_api:object-acl-list',
            kwargs={
                'app_label': self.document_content_type.app_label,
                'model': self.document_content_type.model,
                'object_id': self.document.pk
            }, data={
                'role_pk': self.test_role.pk,
                'permissions_pk_list': permission_acl_view.pk

            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            self.document.acls.first().content_object, self.document
        )
        self.assertEqual(
            self.document.acls.first().role, self.test_role
        )
        self.assertEqual(
            self.document.acls.first().permissions.first(),
            permission_acl_view.stored_permission
        )

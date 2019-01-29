from __future__ import unicode_literals

from django.utils.encoding import force_text

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..models import Tag
from ..permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)

from .literals import (
    TEST_TAG_COLOR, TEST_TAG_COLOR_EDITED, TEST_TAG_LABEL,
    TEST_TAG_LABEL_EDITED
)
from .mixins import TagTestMixin, TagViewTestMixin


class TagViewTestCase(TagViewTestMixin, TagTestMixin, GenericViewTestCase):
    def test_tag_create_view_no_permissions(self):
        response = self._request_tag_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(Tag.objects.count(), 0)

    def test_tag_create_view_with_permissions(self):
        self.grant_permission(permission=permission_tag_create)
        response = self._request_tag_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Tag.objects.count(), 1)
        tag = Tag.objects.first()
        self.assertEqual(tag.label, TEST_TAG_LABEL)
        self.assertEqual(tag.color, TEST_TAG_COLOR)

    def test_tag_delete_view_no_permissions(self):
        self._create_test_tag()

        response = self._request_tag_delete_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tag.objects.count(), 1)

    def test_tag_delete_view_with_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_delete)

        response = self._request_tag_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Tag.objects.count(), 0)

    def test_tag_multiple_delete_view_no_permissions(self):
        self._create_test_tag()

        response = self._request_tag_multiple_delete_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tag.objects.count(), 1)

    def test_tag_multiple_delete_view_with_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_delete)

        response = self._request_tag_multiple_delete_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tag.objects.count(), 0)

    def test_tag_edit_view_no_permissions(self):
        self._create_test_tag()

        response = self._request_tag_edit_view()
        self.assertEqual(response.status_code, 404)
        tag = Tag.objects.get(pk=self.test_tag.pk)
        self.assertEqual(tag.label, TEST_TAG_LABEL)
        self.assertEqual(tag.color, TEST_TAG_COLOR)

    def test_tag_edit_view_with_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_edit)

        response = self._request_tag_edit_view()
        self.assertEqual(response.status_code, 302)
        tag = Tag.objects.get(pk=self.test_tag.pk)
        self.assertEqual(tag.label, TEST_TAG_LABEL_EDITED)
        self.assertEqual(tag.color, TEST_TAG_COLOR_EDITED)


class TagDocumentsViewTestCase(TagViewTestMixin, TagTestMixin, GenericDocumentViewTestCase):
    def test_document_tag_attach_view_no_permission(self):
        self._create_test_tag()

        response = self._request_document_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_tag_attach_view_with_document_access(self):
        self._create_test_tag()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        response = self._request_document_tag_multiple_attach_view()
        self.assertContains(
            response=response, text=force_text(self.test_document),
            status_code=200
        )
        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=200
        )

        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_tag_attach_view_with_tag_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_document_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_tag_attach_view_with_full_access(self):
        self._create_test_tag()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_document_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(
            self.test_document.tags.all(), (repr(self.test_tag),)
        )


    def test_document_single_tag_attach_view_with_full_access(self):
        """
        Test to make sure only the tag is attached to the selected document
        """
        self._create_test_tag()
        self.test_document_2 = self.upload_document()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        self.grant_access(
            obj=self.test_document_2, permission=permission_tag_attach
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_document_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(
            self.test_document.tags.all(), (repr(self.test_tag),)
        )

        self.assertEqual(self.test_document_2.tags.count(), 0)

    def test_document_multiple_tag_attach_view_no_permission(self):
        self._create_test_tag()

        response = self._request_document_multiple_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_multiple_tag_attach_view_with_document_access(self):
        self._create_test_tag()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )

        response = self._request_document_multiple_tag_multiple_attach_view()

        self.assertContains(
            response=response, text=force_text(self.test_document),
            status_code=200
        )
        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=200
        )

        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_multiple_tag_attach_view_with_tag_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)

        response = self._request_document_multiple_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_multiple_tag_attach_view_with_full_access(self):
        self._create_test_tag()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)

        response = self._request_document_multiple_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(
            self.test_document.tags.all(), (repr(self.test_tag),)
        )

    def test_document_tag_multiple_remove_view_no_permissions(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        response = self._request_document_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 404)

        self.assertQuerysetEqual(
            self.test_document.tags.all(), (repr(self.test_tag),)
        )

    def test_document_tag_multiple_remove_view_with_document_access(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )
        response = self._request_document_tag_multiple_remove_view()
        self.assertNotContains(
            response=response, text=self.test_tag, status_code=200
        )
        self.assertContains(
            response=response, text=self.test_document, status_code=200
        )

        self.assertEqual(self.test_document.tags.count(), 1)

    def test_document_tag_multiple_remove_view_with_tag_access(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)

        response = self._request_document_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(self.test_document.tags.count(), 1)

    def test_document_tag_multiple_remove_view_with_full_access(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)

        response = self._request_document_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_tags_list_no_permissions(self):
        self._create_test_tag()

        self.test_tag.documents.add(self.test_document)

        response = self._request_document_tag_list_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=404
        )

    def test_document_tags_list_with_document_access(self):
        self._create_test_tag()

        self.test_tag.documents.add(self.test_document)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_view
        )

        response = self._request_document_tag_list_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=200
        )

    def test_document_tags_list_with_tag_access(self):
        self._create_test_tag()

        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_view)

        response = self._request_document_tag_list_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=404
        )

    def test_document_tags_list_with_full_access(self):
        self._create_test_tag()

        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        self.grant_access(
            obj=self.test_document, permission=permission_tag_view
        )

        response = self._request_document_tag_list_view()
        self.assertContains(
            response=response, text=force_text(self.test_tag), status_code=200
        )

    def test_document_multiple_tag_remove_view_no_permissions(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        response = self._request_document_multiple_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 404)

        self.assertQuerysetEqual(
            self.test_document.tags.all(), (repr(self.test_tag),)
        )

    def test_document_multiple_tag_remove_view_with_full_access(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)

        response = self._request_document_multiple_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.test_document.tags.count(), 0)

from __future__ import unicode_literals

import time

from django.urls import reverse

from ..links import (
    link_trashed_document_restore, link_document_version_download,
    link_document_version_revert
)
from ..models import TrashedDocument
from ..permissions import (
    permission_document_download, permission_trashed_document_restore,
    permission_document_version_revert
)

from .base import GenericDocumentViewTestCase
from .literals import TEST_SMALL_DOCUMENT_PATH


class DocumentsLinksTestCase(GenericDocumentViewTestCase):
    def test_document_version_revert_link_no_permission(self):
        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
            self.document.new_version(file_object=file_object)

        self.assertTrue(self.document.versions.count(), 2)

        self.add_test_view(test_object=self.document.versions.first())
        context = self.get_test_view()
        resolved_link = link_document_version_revert.resolve(context=context)

        self.assertEqual(resolved_link, None)

    def test_document_version_revert_link_with_access(self):
        # Needed by MySQL as milliseconds value is not store in timestamp
        # field
        time.sleep(1.01)

        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
            self.document.new_version(file_object=file_object)

        self.assertTrue(self.document.versions.count(), 2)

        self.grant_access(
            obj=self.document, permission=permission_document_version_revert
        )

        self.add_test_view(test_object=self.document.versions.first())
        context = self.get_test_view()
        resolved_link = link_document_version_revert.resolve(context=context)

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='documents:document_version_revert',
                kwargs={'document_version_id': self.document.versions.first().pk}
            )
        )

    def test_document_version_download_link_no_permission(self):
        self.add_test_view(test_object=self.document.latest_version)
        context = self.get_test_view()
        resolved_link = link_document_version_download.resolve(context=context)

        self.assertEqual(resolved_link, None)

    def test_document_version_download_link_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_download
        )

        self.add_test_view(test_object=self.document.latest_version)
        context = self.get_test_view()
        resolved_link = link_document_version_download.resolve(context=context)

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='documents:document_version_download_form',
                kwargs={'document_version_id': self.document.latest_version.pk}
            )
        )


class DeletedDocumentsLinksTestCase(GenericDocumentViewTestCase):
    def _request_trashed_document_restore_link(self):
        self.add_test_view(
            test_object=TrashedDocument.objects.get(pk=self.document.pk)
        )
        context = self.get_test_view()
        return link_trashed_document_restore.resolve(context=context)

    def test_deleted_document_restore_link_no_permission(self):
        self.document.delete()

        resolved_link = self._request_trashed_document_restore_link()

        self.assertEqual(resolved_link, None)

    def test_deleted_document_restore_link_with_access(self):
        self.document.delete()

        self.grant_access(
            obj=self.document, permission=permission_trashed_document_restore
        )

        resolved_link = self._request_trashed_document_restore_link()

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='documents:trashed_document_restore',
                kwargs={'trashed_document_id': self.document.pk}
            )
        )

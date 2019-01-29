from __future__ import unicode_literals

from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_create
from mayan.apps.documents.tests import (
    GenericDocumentViewTestCase, TEST_SMALL_DOCUMENT_PATH,
)
from mayan.apps.sources.models import WebFormSource
from mayan.apps.sources.tests.literals import (
    TEST_SOURCE_LABEL, TEST_SOURCE_UNCOMPRESS_N
)

from ..models import Tag

from .literals import TEST_TAG_COLOR, TEST_TAG_LABEL
from .mixins import TagTestMixin


class TaggedDocumentUploadTestCase(TagTestMixin, GenericDocumentViewTestCase):
    def setUp(self):
        super(TaggedDocumentUploadTestCase, self).setUp()
        self.source = WebFormSource.objects.create(
            enabled=True, label=TEST_SOURCE_LABEL,
            uncompress=TEST_SOURCE_UNCOMPRESS_N
        )

        self.document.delete()

    def _request_upload_interactive_document_create_view(self):
        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
            return self.post(
                viewname='sources:upload_interactive',
                kwargs={'source_id': self.source.pk},
                data={
                    'document_type_id': self.document_type.pk,
                    'source-file': file_object,
                    'tags': self.test_tag.pk
                }
            )

    def test_upload_interactive_view_with_access(self):
        self._create_test_tag()
        self.grant_access(
            permission=permission_document_create, obj=self.document_type
        )
        response = self._request_upload_interactive_document_create_view()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.test_tag in Document.objects.first().tags.all())

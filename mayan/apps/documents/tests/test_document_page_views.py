from __future__ import unicode_literals

from django.utils.encoding import force_text

from ..permissions import permission_document_view

from .base import GenericDocumentViewTestCase
from .literals import TEST_MULTI_PAGE_TIFF


class DocumentPageViewTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentPageViewTestCase, self).setUp()
        self.login_user()

    def _document_page_list_view(self):
        return self.get(
            viewname='documents:document_pages',
            kwargs={'document_pk': self.document.pk}
        )

    def test_document_page_list_view_no_permission(self):
        response = self._document_page_list_view()
        self.assertEqual(response.status_code, 403)

    def test_document_page_list_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        response = self._document_page_list_view()
        self.assertContains(
            response=response, text=self.document.label, status_code=200
        )


class DocumentPageNavigationViewTestCase(GenericDocumentViewTestCase):
    test_document_filename = TEST_MULTI_PAGE_TIFF

    def setUp(self):
        super(DocumentPageNavigationViewTestCase, self).setUp()
        self.login_user()

    def _request_document_page_navigation_next_view(self):
        return self.get(
            viewname='documents:document_page_navigation_next',
            kwargs={'document_page_pk': self.document.pages.first().pk},
            follow=True
        )

    def test_document_page_navigation_next_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )

        response = self._request_document_page_navigation_next_view()

        self.assertContains(
            response=response, status_code=200,
            text=force_text(self.document.pages.last())
        )

    def _request_document_page_navigation_last_view(self):
        return self.get(
            viewname='documents:document_page_navigation_last',
            kwargs={'document_page_pk': self.document.pages.first().pk},
            follow=True
        )

    def test_document_page_navigation_last_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )

        response = self._request_document_page_navigation_last_view()

        self.assertContains(
            response=response, status_code=200,
            text=force_text(self.document.pages.last())
        )

    def _request_document_page_navigation_previous_view(self):
        return self.get(
            viewname='documents:document_page_navigation_previous',
            kwargs={'document_page_pk': self.document.pages.last().pk},
            follow=True
        )

    def test_document_page_navigation_previous_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )

        response = self._request_document_page_navigation_previous_view()

        self.assertContains(
            response=response, status_code=200,
            text=force_text(self.document.pages.first())
        )

    def _request_document_page_navigation_first_view(self):
        return self.get(
            viewname='documents:document_page_navigation_first',
            kwargs={'document_page_pk': self.document.pages.last().pk},
            follow=True
        )

    def test_document_page_navigation_first_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )

        response = self._request_document_page_navigation_first_view()

        self.assertContains(
            response=response, status_code=200,
            text=force_text(self.document.pages.first())
        )

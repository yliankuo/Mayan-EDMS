from __future__ import unicode_literals

from mayan.apps.rest_api.tests import BaseAPITestCase

from .mixins import EventTypeTestMixin


class EventTypeNamespaceAPITestCase(EventTypeTestMixin, BaseAPITestCase):
    def setUp(self):
        super(EventTypeNamespaceAPITestCase, self).setUp()
        self._create_test_event_type()

    def test_event_type_namespace_list_view(self):
        response = self.get(viewname='rest_api:event_type_namespace-list')
        self.assertEqual(response.status_code, 200)

    def test_event_type_namespace_event_type_list_view(self):
        response = self.get(
            viewname='rest_api:event_type_namespace-event_type-list',
            kwargs={
                'event_type_namespace_name': self.test_event_type_namespace.name
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_event_type_list_view(self):
        response = self.get(
            viewname='rest_api:event_type-detail',
            kwargs={
                'event_type_namespace_name': self.test_event_type_namespace.name,
                'event_type_id': self.test_event_type.id
            }
        )
        self.assertEqual(response.status_code, 200)

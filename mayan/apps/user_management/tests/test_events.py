from __future__ import unicode_literals

from actstream.models import Action

from mayan.apps.common.tests import GenericViewTestCase

from ..permissions import (
    permission_group_create, permission_group_edit, permission_user_create,
    permission_user_edit
)

from ..events import (
    event_group_created, event_group_edited, event_user_created,
    event_user_edited
)

from .mixins import GroupTestMixin, UserTestMixin


class GroupEventsTestCase(GroupTestMixin, UserTestMixin, GenericViewTestCase):
    def test_group_create_event(self):
        Action.objects.all().delete()

        self.grant_permission(
            permission=permission_group_create
        )
        self._request_test_group_create_view()
        self.assertEqual(Action.objects.last().target, self.test_group)
        self.assertEqual(Action.objects.last().verb, event_group_created.id)

    def test_group_edit_event(self):
        self._create_test_group()
        Action.objects.all().delete()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        self._request_test_group_edit_view()
        self.assertEqual(Action.objects.last().target, self.test_group)
        self.assertEqual(Action.objects.last().verb, event_group_edited.id)


class UserEventsTestCase(UserTestMixin, GenericViewTestCase):
    def test_user_create_event(self):
        Action.objects.all().delete()

        self.grant_permission(
            permission=permission_user_create
        )
        self._request_test_user_create_view()
        self.assertEqual(Action.objects.last().target, self.test_user)
        self.assertEqual(Action.objects.last().verb, event_user_created.id)

    def test_user_edit_event(self):
        self._create_test_user()
        Action.objects.all().delete()

        self.grant_access(
            obj=self.test_user, permission=permission_user_edit
        )
        self._request_test_user_edit_view()
        self.assertEqual(Action.objects.last().target, self.test_user)
        self.assertEqual(Action.objects.last().verb, event_user_edited.id)

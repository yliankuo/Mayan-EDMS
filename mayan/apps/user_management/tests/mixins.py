from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .literals import (
    TEST_CASE_ADMIN_EMAIL, TEST_CASE_ADMIN_PASSWORD, TEST_CASE_ADMIN_USERNAME,
    TEST_CASE_GROUP_NAME, TEST_CASE_USER_EMAIL, TEST_CASE_USER_PASSWORD,
    TEST_CASE_USER_USERNAME, TEST_GROUP_NAME, TEST_GROUP_2_NAME,
    TEST_GROUP_2_NAME_EDITED, TEST_USER_2_EMAIL, TEST_USER_2_PASSWORD,
    TEST_USER_EMAIL, TEST_USER_USERNAME, TEST_USER_PASSWORD,
    TEST_USER_2_USERNAME, TEST_USER_2_USERNAME_EDITED
)


class UserTestCaseMixin(object):
    auto_login_admin = False
    auto_login_user = True

    def setUp(self):
        super(UserTestCaseMixin, self).setUp()
        if self.auto_login_user:
            self._test_case_user = get_user_model().objects.create_user(
                username=TEST_CASE_USER_USERNAME, email=TEST_CASE_USER_EMAIL,
                password=TEST_CASE_USER_PASSWORD
            )
            self.login_user()
            self._test_case_group = Group.objects.create(name=TEST_GROUP_NAME)
            self._test_case_group.user_set.add(self._test_case_user)
        elif self.auto_login_admin:
            self._test_case_admin_user = get_user_model().objects.create_superuser(
                username=TEST_CASE_ADMIN_USERNAME, email=TEST_CASE_ADMIN_EMAIL,
                password=TEST_CASE_ADMIN_PASSWORD
            )
            self.login_admin_user()

    def tearDown(self):
        self.client.logout()
        super(UserTestCaseMixin, self).tearDown()

    def login(self, *args, **kwargs):
        logged_in = self.client.login(*args, **kwargs)

        return logged_in

    def login_user(self):
        self.login(
            username=TEST_CASE_USER_USERNAME, password=TEST_CASE_USER_PASSWORD
        )

    def login_admin_user(self):
        self.login(
            username=TEST_CASE_ADMIN_USERNAME,
            password=TEST_CASE_ADMIN_PASSWORD
        )

    def logout(self):
        self.client.logout()


class UserTestMixin(object):
    def _create_test_group(self):
        self.test_group = Group.objects.create(name=TEST_GROUP_2_NAME)

    def _edit_test_group(self):
        self.test_group.name = TEST_GROUP_2_NAME_EDITED
        self.test_group.save()

    def _create_test_user(self):
        self.test_user = get_user_model().objects.create(
            username=TEST_USER_2_USERNAME, email=TEST_USER_2_EMAIL,
            password=TEST_USER_2_PASSWORD
        )

    # Group views

    def _request_test_group_create_view(self):
        reponse = self.post(
            viewname='user_management:group_create', data={
                'name': TEST_GROUP_2_NAME
            }
        )
        self.test_group = Group.objects.filter(name=TEST_GROUP_2_NAME).first()
        return reponse

    def _request_test_group_delete_view(self):
        return self.post(
            viewname='user_management:group_delete', kwargs={
                'group_pk': self.test_group.pk
            }
        )

    def _request_test_group_edit_view(self):
        return self.post(
            viewname='user_management:group_edit', kwargs={
                'group_pk': self.test_group.pk
            }, data={
                'name': TEST_GROUP_2_NAME_EDITED
            }
        )

    def _request_test_group_list_view(self):
        return self.get(viewname='user_management:group_list')

    def _request_test_group_members_view(self):
        return self.get(
            viewname='user_management:group_members',
            kwargs={'group_pk': self.test_group.pk}
        )

    # User views

    def _request_test_user_create_view(self):
        reponse = self.post(
            viewname='user_management:user_create', data={
                'username': TEST_USER_2_USERNAME,
                'password': TEST_USER_2_PASSWORD
            }
        )

        self.test_user = get_user_model().objects.filter(
            username=TEST_USER_2_USERNAME
        ).first()
        return reponse

    def _request_test_user_delete_view(self):
        return self.post(
            viewname='user_management:user_delete',
            kwargs={'user_pk': self.test_user.pk}
        )

    def _request_test_user_edit_view(self):
        return self.post(
            viewname='user_management:user_edit', kwargs={
                'user_pk': self.test_user.pk
            }, data={
                'username': TEST_USER_2_USERNAME_EDITED
            }
        )

    def _request_test_user_groups_view(self):
        return self.get(
            viewname='user_management:user_groups',
            kwargs={'user_pk': self.test_user.pk}
        )

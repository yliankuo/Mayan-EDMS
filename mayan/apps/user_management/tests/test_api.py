from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import status

from mayan.apps.rest_api.tests import BaseAPITestCase

from ..permissions import (
    permission_group_create, permission_group_delete,
    permission_group_edit, permission_group_view,
    permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)

from .literals import (
    TEST_GROUP_2_NAME, TEST_GROUP_2_NAME_EDITED, TEST_USER_2_EMAIL,
    TEST_USER_2_PASSWORD, TEST_USER_2_USERNAME, TEST_USER_2_USERNAME_EDITED,
    TEST_USER_2_PASSWORD_EDITED
)
from .mixins import UserTestMixin


class UserAPITestCase(UserTestMixin, BaseAPITestCase):
    def setUp(self):
        super(UserAPITestCase, self).setUp()
        self.login_user()

    def _request_api_test_user_create(self):
        return self.post(
            viewname='rest_api:user-list', data={
                'email': TEST_USER_2_EMAIL, 'password': TEST_USER_2_PASSWORD,
                'username': TEST_USER_2_USERNAME,
            }
        )

    def test_user_create_no_permission(self):
        response = self._request_api_test_user_create()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Default two users, the test admin and the test user
        self.assertEqual(get_user_model().objects.count(), 2)

    def test_user_create_with_permission(self):
        self.grant_permission(permission=permission_user_create)
        response = self._request_api_test_user_create()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(pk=response.data['id'])
        self.assertEqual(user.username, TEST_USER_2_USERNAME)
        self.assertEqual(get_user_model().objects.count(), 3)

    def _request_api_create_test_user_with_extra_data(self):
        return self.post(
            viewname='rest_api:user-list', data={
                'email': TEST_USER_2_EMAIL, 'password': TEST_USER_2_PASSWORD,
                'username': TEST_USER_2_USERNAME,
                'groups_id_list': self.test_groups_id_list
            }
        )

    """
    def test_user_create_with_group_no_permission(self):
        self._create_test_group()
        self.test_groups_id_list = '{}'.format(self.test_group.pk)

        response = self._request_api_create_test_user_with_extra_data()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_create_with_group_with_user_access(self):
        self._create_test_group()
        self.test_groups_id_list = '{}'.format(self.test_group.pk)

        self.grant_access(
            obj=self.test_user, permission=permission_user_create
        )
        response = self._request_api_create_test_user_with_extra_data()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(pk=response.data['id'])
        self.assertEqual(user.username, TEST_USER_2_USERNAME)
        self.assertQuerysetEqual(user.groups.all(), (repr(self.test_group),))


    def test_user_create_with_group_with_user_access(self):
        self._create_test_group()
        self.test_groups_id_list = '{}'.format(self.test_group.pk)

        self.grant_access(
            obj=self.test_user, permission=permission_user_create
        )
        response = self._request_api_create_test_user_with_extra_data()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(pk=response.data['id'])
        self.assertEqual(user.username, TEST_USER_2_USERNAME)
        self.assertQuerysetEqual(user.groups.all(), (repr(self.test_group),))
    """

    def test_user_create_with_groups_no_permission(self):
        group_1 = Group.objects.create(name='test group 1')
        group_2 = Group.objects.create(name='test group 2')
        self.test_groups_id_list = '{},{}'.format(group_1.pk, group_2.pk)
        response = self._request_api_create_test_user_with_extra_data()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_create_with_groups_with_user_permission(self):
        group_1 = Group.objects.create(name='test group 1')
        group_2 = Group.objects.create(name='test group 2')
        self.test_groups_id_list = '{},{}'.format(group_1.pk, group_2.pk)
        self.grant_permission(permission=permission_user_create)
        response = self._request_api_create_test_user_with_extra_data()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(pk=response.data['id'])
        self.assertEqual(user.username, TEST_USER_2_USERNAME)
        #self.assertQuerysetEqual(
        #    user.groups.all().order_by('name'), (repr(group_1), repr(group_2))
        #)
        self.assertEqual(user.groups.count(), 0)

    def test_user_create_with_groups_with_full_access(self):
        group_1 = Group.objects.create(name='test group 1')
        group_2 = Group.objects.create(name='test group 2')
        self.test_groups_id_list = '{},{}'.format(group_1.pk, group_2.pk)
        self.grant_permission(permission=permission_user_create)
        self.grant_access(obj=group_1, permission=permission_group_edit)
        self.grant_access(obj=group_2, permission=permission_group_edit)
        response = self._request_api_create_test_user_with_extra_data()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(pk=response.data['id'])
        self.assertEqual(user.username, TEST_USER_2_USERNAME)
        self.assertQuerysetEqual(
            user.groups.all().order_by('name'), (repr(group_1), repr(group_2))
        )

    # User login

    def test_user_create_login(self):
        self._create_test_user()

        self.assertTrue(
            self.login(
                username=TEST_USER_2_USERNAME, password=TEST_USER_2_PASSWORD
            )
        )

    # User password change

    def _request_api_user_password_change(self):
        return self.patch(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk}, data={
                'password': TEST_USER_2_PASSWORD_EDITED,
            }
        )

    def test_user_create_login_password_change_no_access(self):
        self._create_test_user()
        self._request_api_user_password_change()

        self.assertFalse(
            self.client.login(
                username=TEST_USER_2_USERNAME,
                password=TEST_USER_2_PASSWORD_EDITED
            )
        )

    def test_user_create_login_password_change_with_access(self):
        self._create_test_user()

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        self._request_api_user_password_change()

        self.assertTrue(
            self.client.login(
                username=TEST_USER_2_USERNAME,
                password=TEST_USER_2_PASSWORD_EDITED
            )
        )

    # User edit

    def _request_api_test_user_edit_via_put(self):
        return self.put(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk},
            data={'username': TEST_USER_2_USERNAME_EDITED}
        )

    def test_user_edit_via_put_no_access(self):
        self._create_test_user()
        response = self._request_api_test_user_edit_via_put()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, TEST_USER_2_USERNAME)

    def test_user_edit_via_put_with_access(self):
        self._create_test_user()
        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_api_test_user_edit_via_put()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, TEST_USER_2_USERNAME_EDITED)

    def _request_api_test_user_edit_via_patch(self):
        return self.patch(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk},
            data={'username': TEST_USER_2_USERNAME_EDITED}
        )

    def test_user_edit_via_patch_no_access(self):
        self._create_test_user()
        response = self._request_api_test_user_edit_via_patch()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, TEST_USER_2_USERNAME)

    def test_user_edit_via_patch_with_access(self):
        self._create_test_user()
        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_api_test_user_edit_via_patch()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, TEST_USER_2_USERNAME_EDITED)

    def _request_api_test_user_edit_via_patch_with_extra_data(self):
        return self.patch(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk},
            data={'groups_id_list': '{}'.format(self.test_group.pk)}
        )

    def test_user_edit_add_groups_via_patch_no_access(self):
        self._create_test_group()
        self._create_test_user()

        response = self._request_api_test_user_edit_via_patch_with_extra_data()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, TEST_USER_2_USERNAME)

        self.assertQuerysetEqual(
            self.test_user.groups.all(), ()
        )

    def test_user_edit_add_groups_via_patch_with_access(self):
        self._create_test_group()
        self._create_test_user()
        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        self.grant_access(obj=self.test_group, permission=permission_group_edit)
        response = self._request_api_test_user_edit_via_patch_with_extra_data()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, TEST_USER_2_USERNAME)

        self.assertQuerysetEqual(
            self.test_user.groups.all(), (repr(self.test_group),)
        )

    # User delete

    def _request_api_test_user_delete(self):
        return self.delete(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk}
        )

    def test_user_delete_no_access(self):
        self._create_test_user()
        response = self._request_api_test_user_delete()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(
            get_user_model().objects.filter(pk=self.test_user.pk).exists()
        )

    def test_user_delete_with_access(self):
        self._create_test_user()
        self.grant_access(
            obj=self.test_user, permission=permission_user_delete
        )
        response = self._request_api_test_user_delete()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            get_user_model().objects.filter(pk=self.test_user.pk).exists()
        )

    # User group listview

    def _request_api_test_user_group_view(self):
        return self.get(
            viewname='rest_api:users-group-list',
            kwargs={'user_id': self.test_user.pk}
        )

    def test_user_group_list_no_access(self):
        group = Group.objects.create(name=TEST_GROUP_2_NAME)
        self._create_test_user()
        self.test_user.groups.add(group)
        response = self._request_api_test_user_group_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_group_list_with_user_access(self):
        group = Group.objects.create(name=TEST_GROUP_2_NAME)
        self._create_test_user()
        self.test_user.groups.add(group)
        self.grant_access(obj=self.test_user, permission=permission_user_view)
        response = self._request_api_test_user_group_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_user_group_list_with_group_access(self):
        self._create_test_group()
        self._create_test_user()
        self.test_user.groups.add(self.test_group)
        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_api_test_user_group_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_group_list_with_access(self):
        self._create_test_group()
        self._create_test_user()
        self.test_user.groups.add(self.test_group)
        self.grant_access(obj=self.test_user, permission=permission_user_view)
        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_api_test_user_group_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def _request_api_test_user_group_add(self):
        return self.patch(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk},
            data={'group_id_list': '{}'.format(self.test_group.pk)}
        )

    def test_user_group_add_no_access(self):
        self._create_test_group()
        self._create_test_user()
        response = self._request_api_test_user_group_add()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_group.user_set.first(), None)

    def test_user_group_add_with_user_access(self):
        self._create_test_group()
        self._create_test_user()
        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_api_test_user_group_add()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_group.user_set.first(), None)

    def test_user_group_add_with_group_access(self):
        self._create_test_group()
        self._create_test_user()
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_api_test_user_group_add()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_group.user_set.first(), None)

    def test_user_group_add_with_full_access(self):
        self._create_test_group()
        self._create_test_user()
        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_api_test_user_group_add()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_group.user_set.first(), self.test_user)


class GroupAPITestCase(UserTestMixin, BaseAPITestCase):
    def setUp(self):
        super(GroupAPITestCase, self).setUp()
        self.login_user()

    def _request_api_test_group_create_view(self):
        return self.post(
            viewname='rest_api:group-list', data={
                'name': TEST_GROUP_2_NAME
            }
        )

    def test_group_create_no_permission(self):
        response = self._request_api_test_group_create_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            TEST_GROUP_2_NAME in list(
                Group.objects.values_list('name', flat=True)
            )
        )

    def test_group_create_with_permission(self):
        self.grant_permission(permission=permission_group_create)
        response = self._request_api_test_group_create_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            TEST_GROUP_2_NAME in list(
                Group.objects.values_list('name', flat=True)
            )
        )

    def _request_api_test_group_delete_view(self):
        return self.delete(
            viewname='rest_api:group-detail',
            kwargs={'group_id': self.test_group.pk}
        )

    def test_group_delete_no_access(self):
        self._create_test_group()
        response = self._request_api_test_group_delete_view()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            TEST_GROUP_2_NAME in list(
                Group.objects.values_list('name', flat=True)
            )
        )

    def test_group_delete_with_access(self):
        self._create_test_group()
        self.grant_access(
            obj=self.test_group, permission=permission_group_delete
        )
        response = self._request_api_test_group_delete_view()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            TEST_GROUP_2_NAME in list(
                Group.objects.values_list('name', flat=True)
            )
        )

    def _request_api_test_group_detail_view(self):
        return self.get(
            viewname='rest_api:group-detail',
            kwargs={'group_id': self.test_group.pk}
        )

    def test_group_detail_no_access(self):
        self._create_test_group()
        response = self._request_api_test_group_detail_view()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(
            self.test_group.name, response.data.get('name', None)
        )

    def test_group_detail_with_access(self):
        self._create_test_group()
        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_api_test_group_detail_view()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_group.name, response.data.get('name', None))


    def _request_api_test_group_edit_via_patch_view(self):
        return self.patch(
            viewname='rest_api:group-detail',
            kwargs={'group_id': self.test_group.pk},
            data={
                'name': TEST_GROUP_2_NAME_EDITED
            }
        )

    def test_group_edit_via_patch_no_access(self):
        self._create_test_group()
        response = self._request_api_test_group_edit_via_patch_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertEqual(self.test_group.name, TEST_GROUP_2_NAME)

    def test_group_edit_via_patch_with_access(self):
        self._create_test_group()
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_api_test_group_edit_via_patch_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertEqual(self.test_group.name, TEST_GROUP_2_NAME_EDITED)

    def _request_api_test_group_list_view(self):
        return self.get(viewname='rest_api:group-list')

    def test_group_list_no_access(self):
        self._create_test_group()
        response = self._request_api_test_group_list_view()
        self.assertNotContains(
            response=response, text=self.test_group.name,
            status_code=status.HTTP_200_OK
        )

    def test_group_list_with_access(self):
        self._create_test_group()
        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_api_test_group_list_view()
        self.assertContains(
            response=response, text=self.test_group.name,
            status_code=status.HTTP_200_OK
        )

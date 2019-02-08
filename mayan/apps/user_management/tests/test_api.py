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
    TEST_GROUP_NAME, TEST_GROUP_NAME_EDITED, TEST_USER_EMAIL, TEST_USER_USERNAME,
    TEST_USER_USERNAME_EDITED, TEST_USER_PASSWORD, TEST_USER_PASSWORD_EDITED
)
from .mixins import GroupTestMixin, UserTestMixin


class GroupAPITestCase(UserTestMixin, GroupTestMixin, BaseAPITestCase):
    def _request_test_group_create_api_view(self):
        return self.post(
            viewname='rest_api:group-list', data={
                'name': TEST_GROUP_NAME
            }
        )

    def test_group_create_api_view_no_permission(self):
        group_count = Group.objects.count()

        response = self._request_test_group_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(group_count, Group.objects.count())

    def test_group_create_api_view_with_permission(self):
        group_count = Group.objects.count()

        self.grant_permission(permission=permission_group_create)
        response = self._request_test_group_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertNotEqual(group_count, Group.objects.count())

    def _request_test_group_delete_api_view(self):
        return self.delete(
            viewname='rest_api:group-detail',
            kwargs={'group_id': self.test_group.pk}
        )

    def test_group_delete_api_view_no_permission(self):
        self._create_test_group()

        group_count = Group.objects.count()

        response = self._request_test_group_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(group_count, Group.objects.count())

    def test_group_delete_api_view_with_access(self):
        self._create_test_group()

        group_count = Group.objects.count()

        self.grant_access(
            obj=self.test_group, permission=permission_group_delete
        )
        response = self._request_test_group_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertNotEqual(group_count, Group.objects.count())

    def _request_test_group_detail_api_view(self):
        return self.get(
            viewname='rest_api:group-detail',
            kwargs={'group_id': self.test_group.pk}
        )

    def test_group_detail_api_view_no_permission(self):
        self._create_test_group()

        response = self._request_test_group_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertNotEqual(
            self.test_group.name, response.data.get('name', None)
        )

    def test_group_detail_api_view_with_access(self):
        self._create_test_group()

        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_group_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.test_group.name, response.data.get('name', None))

    def _request_test_group_edit_patch_api_view(self):
        return self.patch(
            viewname='rest_api:group-detail',
            kwargs={'group_id': self.test_group.pk},
            data={
                'name': TEST_GROUP_NAME_EDITED
            }
        )

    def test_group_edit_patch_api_view_no_permission(self):
        self._create_test_group()

        group_name = self.test_group.name

        response = self._request_test_group_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertEqual(group_name, self.test_group.name)

    def test_group_edit_via_patch_with_access(self):
        self._create_test_group()

        group_name = self.test_group.name

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_group_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertNotEqual(group_name, self.test_group.name)

    def _request_test_group_list_api_view(self):
        return self.get(viewname='rest_api:group-list')

    def test_group_list_api_view_no_permission(self):
        self._create_test_group()

        response = self._request_test_group_list_api_view()
        self.assertNotContains(
            response=response, text=self.test_group.name,
            status_code=status.HTTP_200_OK
        )

    def test_group_list_api_view_with_access(self):
        self._create_test_group()

        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_group_list_api_view()
        self.assertContains(
            response=response, text=self.test_group.name,
            status_code=status.HTTP_200_OK
        )

    def _request_test_group_user_add_patch_api_view(self):
        return self.post(
            viewname='rest_api:group-user-add',
            kwargs={'group_id': self.test_group.pk},
            data={
                'user_id': self.test_user.pk
            }
        )

    def _setup_group_user_add(self):
        self._create_test_group()
        self._create_test_user()

    def test_group_user_add_api_view_no_permission(self):
        self._setup_group_user_add()

        response = self._request_test_group_user_add_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user not in self.test_group.user_set.all())

    def test_group_user_add_with_group_access(self):
        self._setup_group_user_add()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_group_user_add_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user not in self.test_group.user_set.all())

    def test_group_user_add_with_user_access(self):
        self._setup_group_user_add()

        self.grant_access(
            obj=self.test_user, permission=permission_user_edit
        )
        response = self._request_test_group_user_add_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user not in self.test_group.user_set.all())

    def test_group_user_add_with_full_access(self):
        self._setup_group_user_add()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        self.grant_access(
            obj=self.test_user, permission=permission_user_edit
        )
        response = self._request_test_group_user_add_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user in self.test_group.user_set.all())

    #TODO: group-user-list tests

    def _request_test_group_user_remove_patch_api_view(self):
        return self.post(
            viewname='rest_api:group-user-remove',
            kwargs={'group_id': self.test_group.pk},
            data={
                'user_id': self.test_user.pk
            }
        )

    def _setup_group_user_remove(self):
        self._create_test_group()
        self._create_test_user()
        self.test_group.user_set.add(self.test_user)

    def test_group_user_remove_api_view_no_permission(self):
        self._setup_group_user_remove()

        response = self._request_test_group_user_remove_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user in self.test_group.user_set.all())

    def test_group_user_remove_with_group_access(self):
        self._setup_group_user_remove()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_group_user_remove_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user in self.test_group.user_set.all())

    def test_group_user_remove_with_user_access(self):
        self._setup_group_user_remove()

        self.grant_access(
            obj=self.test_user, permission=permission_user_edit
        )
        response = self._request_test_group_user_remove_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user in self.test_group.user_set.all())

    def test_group_user_remove_with_full_access(self):
        self._setup_group_user_remove()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        self.grant_access(
            obj=self.test_user, permission=permission_user_edit
        )
        response = self._request_test_group_user_remove_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user not in self.test_group.user_set.all())


class UserAPITestCase(GroupTestMixin, UserTestMixin, BaseAPITestCase):
    def _request_test_user_create_api_view_api_view(self):
        return self.post(
            viewname='rest_api:user-list', data={
                'email': TEST_USER_EMAIL, 'password': TEST_USER_PASSWORD,
                'username': TEST_USER_USERNAME,
            }
        )

    def test_user_create_api_view_no_permission(self):
        user_count = get_user_model().objects.count()

        response = self._request_test_user_create_api_view_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(user_count, get_user_model().objects.count())

    def test_user_create_api_view_with_permission(self):
        user_count = get_user_model().objects.count()

        self.grant_permission(permission=permission_user_create)
        response = self._request_test_user_create_api_view_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(pk=response.data['id'])

        self.assertEqual(user.username, TEST_USER_USERNAME)
        self.assertEqual(user_count + 1, get_user_model().objects.count())

    def test_user_create_api_view_login(self):
        self._create_test_user()

        self.assertTrue(
            self.login(
                username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
            )
        )

    def _request_user_password_change(self):
        return self.patch(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk}, data={
                'password': TEST_USER_PASSWORD_EDITED,
            }
        )

    def test_user_create_login_password_change_api_view_no_permission(self):
        self._create_test_user()
        self._request_user_password_change()

        self.assertFalse(
            self.client.login(
                username=TEST_USER_USERNAME,
                password=TEST_USER_PASSWORD_EDITED
            )
        )

    def test_user_create_login_password_change_api_view_with_access(self):
        self._create_test_user()

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        self._request_user_password_change()

        self.assertTrue(
            self.client.login(
                username=TEST_USER_USERNAME,
                password=TEST_USER_PASSWORD_EDITED
            )
        )

    def _request_test_user_edit_put_api_view(self):
        return self.put(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk},
            data={'username': TEST_USER_USERNAME_EDITED}
        )

    def test_user_edit_put_api_view_no_permission(self):
        self._create_test_user()
        username = self.test_user.username

        response = self._request_test_user_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertEqual(username, self.test_user.username)

    def test_user_edit_put_api_view_with_access(self):
        self._create_test_user()
        username = self.test_user.username

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_user_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertNotEqual(username, self.test_user.username)

    def _request_test_user_edit_patch_api_view(self):
        return self.patch(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk},
            data={'username': TEST_USER_USERNAME_EDITED}
        )

    def test_user_edit_patch_api_view_no_permission(self):
        self._create_test_user()
        username = self.test_user.username

        response = self._request_test_user_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertEqual(username, self.test_user.username)

    def test_user_edit_patch_api_view_with_access(self):
        self._create_test_user()
        username = self.test_user.username

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_user_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertNotEqual(username, self.test_user.username)

    def _request_test_user_delete_api_view(self):
        return self.delete(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk}
        )

    def test_user_delete_api_view_no_permission(self):
        self._create_test_user()

        response = self._request_test_user_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(
            get_user_model().objects.filter(pk=self.test_user.pk).exists()
        )

    def test_user_delete_api_view_with_access(self):
        self._create_test_user()

        self.grant_access(
            obj=self.test_user, permission=permission_user_delete
        )
        response = self._request_test_user_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            get_user_model().objects.filter(pk=self.test_user.pk).exists()
        )

    def _request_test_user_group_api_view(self):
        return self.get(
            viewname='rest_api:user-group-list',
            kwargs={'user_id': self.test_user.pk}
        )

    def test_user_group_list_api_view_no_permission(self):
        self._create_test_group()
        self._create_test_user()
        self.test_user.groups.add(self.test_group)

        response = self._request_test_user_group_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_group_list_api_view_with_user_access(self):
        self._create_test_group()
        self._create_test_user()
        self.test_user.groups.add(self.test_group)

        self.grant_access(obj=self.test_user, permission=permission_user_view)
        response = self._request_test_user_group_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_user_group_list_api_view_with_group_access(self):
        self._create_test_group()
        self._create_test_user()
        self.test_user.groups.add(self.test_group)

        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_user_group_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_group_list_api_view_with_access(self):
        self._create_test_group()
        self._create_test_user()
        self.test_user.groups.add(self.test_group)

        self.grant_access(obj=self.test_user, permission=permission_user_view)
        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_user_group_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def _request_test_user_group_add_api_view(self):
        return self.patch(
            viewname='rest_api:user-detail',
            kwargs={'user_id': self.test_user.pk},
            data={'group_id_list': '{}'.format(self.test_group.pk)}
        )

    def test_user_group_add_api_view_no_permission(self):
        self._create_test_group()
        self._create_test_user()

        response = self._request_test_user_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_group.user_set.first(), None)

    def test_user_group_add_api_view_with_user_access(self):
        self._create_test_group()
        self._create_test_user()

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_user_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_group.user_set.first(), None)

    def test_user_group_add_api_view_with_group_access(self):
        self._create_test_group()
        self._create_test_user()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_user_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_group.user_set.first(), None)

    def test_user_group_add_api_view_with_full_access(self):
        self._create_test_group()
        self._create_test_user()

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_user_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_group.user_set.first(), self.test_user)

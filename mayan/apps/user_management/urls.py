from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APICurrentUserView, APIGroupListView, APIGroupView, APIUserGroupList,
    APIUserListView, APIUserView
)
from .views import (
    CurrentUserDetailsView, CurrentUserEditView, GroupCreateView,
    GroupDeleteView, GroupEditView, GroupListView, GroupMembersView,
    UserCreateView, UserDeleteView, UserDetailsView, UserEditView,
    UserGroupsView, UserListView, UserOptionsEditView, UserSetPasswordView
)

urlpatterns = [
    url(
        regex=r'^groups/$', name='group_list', view=GroupListView.as_view()
    ),
    url(
        regex=r'^groups/create/$', name='group_create',
        view=GroupCreateView.as_view()
    ),
    url(
        regex=r'^groups/(?P<group_id>\d+)/delete/$', name='group_delete',
        view=GroupDeleteView.as_view()
    ),
    url(
        regex=r'^groups/(?P<group_id>\d+)/edit/$', name='group_edit',
        view=GroupEditView.as_view()
    ),
    url(
        regex=r'^groups/(?P<group_id>\d+)/members/$', name='group_members',
        view=GroupMembersView.as_view()
    ),
    url(
        regex=r'^user/$', name='current_user_details',
        view=CurrentUserDetailsView.as_view()
    ),
    url(
        regex=r'^user/edit/$', name='current_user_edit',
        view=CurrentUserEditView.as_view()
    ),
    url(
        regex=r'^users/$', name='user_list', view=UserListView.as_view()
    ),
    url(
        regex=r'^users/create/$', name='user_create',
        view=UserCreateView.as_view()
    ),
    url(
        regex=r'^users/(?P<user_id>\d+)/$', name='user_details',
        view=UserDetailsView.as_view()
    ),
    url(
        regex=r'^users/(?P<user_id>\d+)/delete/$', name='user_delete',
        view=UserDeleteView.as_view(),
    ),
    url(
        regex=r'^users/(?P<user_id>\d+)/edit/$', name='user_edit',
        view=UserEditView.as_view()
    ),
    url(
        regex=r'^users/(?P<user_id>\d+)/groups/$', name='user_groups',
        view=UserGroupsView.as_view()
    ),
    url(
        regex=r'^users/(?P<user_id>\d+)/options/$', name='user_options',
        view=UserOptionsEditView.as_view()
    ),
    url(
        regex=r'^users/(?P<user_id>\d+)/set_password/$',
        name='user_set_password', view=UserSetPasswordView.as_view()
    ),
    url(
        regex=r'^users/multiple/delete/$', name='user_multiple_delete',
        view=UserDeleteView.as_view()
    ),
    url(
        regex=r'^users/multiple/set_password/$',
        name='user_multiple_set_password', view=UserSetPasswordView.as_view()
    )
]

api_urls = [
    url(
        regex=r'^groups/$', name='group-list', view=APIGroupListView.as_view()
    ),
    url(
        regex=r'^groups/(?P<group_id>\d+)/$', name='group-detail',
        view=APIGroupView.as_view(),
    ),
    url(
        regex=r'^user/$', name='user-current',
        view=APICurrentUserView.as_view()
    ),
    url(regex=r'^users/$', name='user-list', view=APIUserListView.as_view()),
    url(
        regex=r'^users/(?P<user_id>\d+)/$', name='user-detail',
        view=APIUserView.as_view()
    ),
    url(
        regex=r'^users/(?P<user_id>\d+)/groups/$', name='users-group-list',
        view=APIUserGroupList.as_view()
    ),
]

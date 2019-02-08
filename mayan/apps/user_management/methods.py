from __future__ import unicode_literals

from django.apps import apps
from django.db import transaction
from django.shortcuts import reverse

from .events import event_group_edited, event_user_edited
from .permissions import permission_user_view
from .querysets import get_user_queryset


def method_group_get_users(self, _user):
    AccessControlList = apps.get_model(
        app_label='acls', model_name='AccessControlList'
    )

    return AccessControlList.objects.restrict_queryset(
        permission=permission_user_view, queryset=get_user_queryset(),
        user=_user
    )


def method_group_user_add(self, user, _user):
    with transaction.atomic():
        self.user_set.add(user)
        event_group_edited.commit(
            actor=_user, target=self
        )
        event_user_edited.commit(
            actor=_user, target=user
        )


def method_group_user_remove(self, user, _user):
    with transaction.atomic():
        self.user_set.remove(user)
        event_group_edited.commit(
            actor=_user, target=self
        )
        event_user_edited.commit(
            actor=_user, target=user
        )


def method_user_get_absolute_url(self):
    return reverse(
        viewname='user_management:user_details', kwargs={'user_id': self.pk}
    )


def method_user_get_groups(self, _user):
    AccessControlList = apps.get_model(
        app_label='acls', model_name='AccessControlList'
    )

    return AccessControlList.objects.restrict_queryset(
        permission=permission_user_view, queryset=self.groups.all(),
        user=_user
    )

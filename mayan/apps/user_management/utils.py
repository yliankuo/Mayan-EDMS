from __future__ import unicode_literals

from django.apps import apps
from django.contrib.auth import get_user_model


def get_groups():
    Group = apps.get_model(app_label='auth', model_name='Group')
    return ','.join([group.name for group in Group.objects.all()])


def get_users():
    return ','.join(
        [
            user.get_full_name() or user.username
            for user in get_user_model().objects.all()
        ]
    )

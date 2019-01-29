from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from mayan.apps.acls.models import AccessControlList

from .permissions import permission_group_edit, permission_group_view


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users_count = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'group_pk',
                'view_name': 'rest_api:group-detail'
            }
        }
        fields = ('id', 'name', 'url', 'users_count')
        model = Group

    def get_users_count(self, instance):
        return instance.user_set.count()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True, read_only=True, required=False)
    groups_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of group primary keys to assign this '
            'user to.'
        ), required=False, write_only=True
    )
    password = serializers.CharField(
        required=False, style={'input_type': 'password'}, write_only=True
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'user_pk',
                'view_name': 'rest_api:user-detail'
            }
        }
        fields = (
            'first_name', 'date_joined', 'email', 'groups', 'groups_pk_list',
            'id', 'is_active', 'last_login', 'last_name', 'password', 'url',
            'username'
        )
        model = get_user_model()
        read_only_fields = ('groups', 'is_active', 'last_login', 'date_joined')
        write_only_fields = ('password', 'group_pk_list')

    def _add_groups(self, instance, groups_pk_list):
        instance.groups.clear()

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_group_edit,
            queryset=Group.objects.filter(pk__in=groups_pk_list.split(',')),
            user=self.context['request'].user
        )

        instance.groups.add(*queryset)

    def create(self, validated_data):
        groups_pk_list = validated_data.pop('groups_pk_list', '')
        password = validated_data.pop('password', None)
        instance = super(UserSerializer, self).create(validated_data)

        if password:
            instance.set_password(password)
            instance.save()

        if groups_pk_list:
            self._add_groups(instance=instance, groups_pk_list=groups_pk_list)

        return instance

    def update(self, instance, validated_data):
        groups_pk_list = validated_data.pop('groups_pk_list', '')

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            validated_data.pop('password')

        instance = super(UserSerializer, self).update(instance, validated_data)

        if groups_pk_list:
            self._add_groups(instance=instance, groups_pk_list=groups_pk_list)

        return instance

    def validate(self, data):
        if 'password' in data:
            validate_password(data['password'], self.instance)

        return data

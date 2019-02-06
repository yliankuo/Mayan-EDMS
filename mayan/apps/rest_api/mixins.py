from __future__ import absolute_import, unicode_literals

from django.core.exceptions import ImproperlyConfigured

from mayan.apps.acls.models import AccessControlList


class ExternalObjectListSerializerMixin(object):
    class Meta:
        external_object_list_model = None
        external_object_list_permission = None
        external_object_list_queryset = None
        external_object_list_pk_field = None
        external_object_list_pk_list_field = None

    def get_external_object_list(self):
        queryset = self.get_external_object_list_queryset()

        if self.Meta.external_object_list_permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=self.Meta.external_object_list_permission,
                queryset=queryset,
                user=self.context['request'].user
            )

        if self.Meta.external_object_list_pk_field:
            id_list = (
                self.validated_data.get(self.Meta.external_object_list_pk_field),
            )
        elif self.Meta.external_object_list_pk_list_field:
            id_list = self.validated_data.get(
                self.Meta.external_object_list_pk_list_field, ''
            ).split(',')
        else:
            raise ImproperlyConfigured(
                'ExternalObjectListSerializerMixin requires a '
                'external_object_list__pk_field a '
                'external_object_list_pk_list_field.'
            )

        return queryset.filter(pk__in=id_list)

    def get_external_object_list_queryset(self):
        if self.Meta.external_object_list_model:
            queryset = self.Meta.external_object_list_model._meta.default_manager.all()
        elif self.Meta.external_object_list_queryset:
            return self.Meta.external_object_list_queryset
        else:
            raise ImproperlyConfigured(
                'ExternalObjectListSerializerMixin requires a '
                'external_object_list_model or a external_object_list_queryset.'
            )

        return queryset

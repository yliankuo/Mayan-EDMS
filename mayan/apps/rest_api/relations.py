from __future__ import unicode_literals

from rest_framework.relations import HyperlinkedIdentityField

from mayan.apps.common.utils import resolve_attribute


class MultiKwargHyperlinkedIdentityField(HyperlinkedIdentityField):
    def __init__(self, *args, **kwargs):
        self.view_kwargs = kwargs.pop('view_kwargs', [])
        super(MultiKwargHyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        """
        Extends HyperlinkedRelatedField to allow passing more than one view
        keyword argument.
        ----
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        kwargs = {}
        for entry in self.view_kwargs:
            kwargs[entry['lookup_url_kwarg']] = resolve_attribute(
                obj=obj, attribute=entry['lookup_field']
            )

        return self.reverse(
            viewname=view_name, kwargs=kwargs, request=request, format=format
        )

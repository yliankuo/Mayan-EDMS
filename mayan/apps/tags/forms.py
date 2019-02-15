from __future__ import absolute_import, unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.forms import FilteredSelectionForm

from .models import Tag
from .permissions import permission_tag_view
from .widgets import TagFormWidget


class TagMultipleSelectionForm(FilteredSelectionForm):
    class Media:
        js = ('tags/js/tags_form.js',)

    class Meta:
        allow_multiple = True
        field_name = 'tags'
        label = _('Tags')
        required = False
        widget_attributes = {'class': 'select2-tags'}

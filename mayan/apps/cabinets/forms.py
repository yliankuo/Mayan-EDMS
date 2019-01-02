from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.forms import FilteredSelectionForm


class CabinetListForm(FilteredSelectionForm):
    _field_name = 'cabinets'
    _label = _('Cabinets')
    _widget_attributes = {'class': 'select2'}
    _allow_multiple = True

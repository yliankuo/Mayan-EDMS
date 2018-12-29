from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.events import EventTypeNamespace

namespace = EventTypeNamespace(
    name='user_management', label=_('User management')
)

event_group_created = namespace.add_event_type(
    label=_('Group created'), name='created'
)
event_group_edited = namespace.add_event_type(
    label=_('Group edited'), name='edited'
)

event_user_created = namespace.add_event_type(
    label=_('User created'), name='created'
)
event_user_edited = namespace.add_event_type(
    label=_('User edited'), name='edited'
)

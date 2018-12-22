from __future__ import unicode_literals

from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.utils import resolve_attribute

from .classes import EventType


def widget_event_object_link(context, attribute='target'):
    entry = context['object']
    label = ''
    url = '#'
    obj_type = ''

    obj = resolve_attribute(obj=entry, attribute=attribute)

    if obj:
        obj_type = '{}: '.format(obj._meta.verbose_name)
        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
        label = force_text(obj)

    return mark_safe(
        '<a href="%(url)s">%(obj_type)s%(label)s</a>' % {
            'url': url, 'label': label, 'obj_type': obj_type
        }
    )


def widget_event_type_link(context, attribute=None):
    entry = context['object']

    if attribute:
        entry = getattr(entry, attribute)

    return mark_safe(
        '<a href="%(url)s">%(label)s</a>' % {
            'url': reverse('events:events_by_verb', kwargs={'verb': entry.verb}),
            'label': EventType.get(name=entry.verb)
        }
    )


def widget_event_user_link(context, attribute=None):
    entry = context['object']

    if attribute:
        entry = getattr(entry, attribute)

    if entry.actor == entry.target:
        return _('System')
    else:
        return mark_safe(
            '<a href="%(url)s">%(label)s</a>' % {
                'url': reverse('events:user_events', kwargs={'pk': entry.actor.pk}),
                'label': entry.actor
            }
        )

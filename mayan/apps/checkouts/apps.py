from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from kombu import Exchange, Queue

from django.apps import apps
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls import ModelPermission
from mayan.apps.common import (
    MayanAppConfig, menu_facet, menu_main, menu_sidebar
)
from mayan.apps.common.dashboards import dashboard_main
from mayan.apps.events import ModelEventType
from mayan.celery import app

from .dashboard_widgets import DashboardWidgetTotalCheckouts
from .events import (
    event_document_auto_check_in, event_document_check_in,
    event_document_check_out, event_document_forceful_check_in
)
from .handlers import check_new_version_creation
from .links import (
    link_checkin_document, link_checkout_document, link_checkout_info,
    link_checkout_list
)
from .literals import CHECK_EXPIRED_CHECK_OUTS_INTERVAL
from .permissions import (
    permission_document_checkin, permission_document_checkin_override,
    permission_document_checkout, permission_document_checkout_detail_view
)
from .queues import *  # NOQA
# This import is required so that celerybeat can find the task
from .tasks import task_check_expired_check_outs  # NOQA


class CheckoutsApp(MayanAppConfig):
    app_namespace = 'checkouts'
    app_url = 'checkouts'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.checkouts'
    verbose_name = _('Checkouts')

    def ready(self):
        super(CheckoutsApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentVersion = apps.get_model(
            app_label='documents', model_name='DocumentVersion'
        )

        DocumentCheckout = self.get_model('DocumentCheckout')

        Document.add_to_class(
            name='check_in',
            value=lambda document, user=None: DocumentCheckout.objects.check_in_document(document, user)
        )
        Document.add_to_class(
            name='checkout_info',
            value=lambda document: DocumentCheckout.objects.document_checkout_info(
                document
            )
        )
        Document.add_to_class(
            name='checkout_state',
            value=lambda document: DocumentCheckout.objects.document_checkout_state(
                document
            )
        )
        Document.add_to_class(
            name='is_checked_out',
            value=lambda document: DocumentCheckout.objects.is_document_checked_out(
                document
            )
        )

        ModelEventType.register(
            model=Document, event_types=(
                event_document_auto_check_in, event_document_check_in,
                event_document_check_out, event_document_forceful_check_in
            )
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_document_checkout,
                permission_document_checkin,
                permission_document_checkin_override,
                permission_document_checkout_detail_view
            )
        )

        app.conf.beat_schedule.update(
            {
                'task_check_expired_check_outs': {
                    'task': 'mayan.apps.checkouts.tasks.task_check_expired_check_outs',
                    'schedule': timedelta(
                        seconds=CHECK_EXPIRED_CHECK_OUTS_INTERVAL
                    ),
                },
            }
        )

        app.conf.task_queues.append(
            Queue(
                'checkouts_periodic', Exchange('checkouts_periodic'),
                routing_key='checkouts_periodic', delivery_mode=1
            ),
        )

        app.conf.task_routes.update(
            {
                'mayan.apps.checkouts.tasks.task_check_expired_check_outs': {
                    'queue': 'checkouts_periodic'
                },
            }
        )

        dashboard_main.add_widget(
            widget=DashboardWidgetTotalCheckouts, order=-1
        )

        menu_facet.bind_links(links=(link_checkout_info,), sources=(Document,))
        menu_main.bind_links(links=(link_checkout_list,), position=98)
        menu_sidebar.bind_links(
            links=(link_checkout_document, link_checkin_document),
            sources=(
                'checkouts:checkout_info', 'checkouts:checkout_document',
                'checkouts:checkin_document'
            )
        )

        pre_save.connect(
            check_new_version_creation,
            dispatch_uid='check_new_version_creation',
            sender=DocumentVersion
        )

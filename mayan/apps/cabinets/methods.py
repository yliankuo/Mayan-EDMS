from __future__ import unicode_literals

from django.apps import apps


def method_get_document_cabinets(self):
    DocumentCabinet = apps.get_models(
        app_label='cabinets', model_name='DocumentCabinet'
    )

    return DocumentCabinet.objects.filter(documents=self).order_by(
        'parent__label', 'label'
    )

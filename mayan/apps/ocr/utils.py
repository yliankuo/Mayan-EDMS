from __future__ import unicode_literals

from django.apps import apps
from django.utils.encoding import force_text


def get_document_ocr_content(document):
    DocumentPageOCRContent = apps.get_model(
        app_label='ocr', model_name='DocumentPageOCRContent'
    )

    for page in document.pages.all():
        try:
            page_content = page.ocr_content.content
        except DocumentPageOCRContent.DoesNotExist:
            return
        else:
            yield force_text(page_content)


@property
def document_property_ocr_content(self):
    return ' '.join(get_document_ocr_content(self))

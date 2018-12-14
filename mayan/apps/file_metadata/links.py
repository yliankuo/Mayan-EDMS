from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link

from .icons import icon_file_metadata
from .permissions import (
    permission_document_type_file_metadata_setup,
    permission_file_metadata_submit, permission_file_metadata_view
)

link_document_driver_list = Link(
    args='resolved_object.id', icon_class=icon_file_metadata,
    permissions=(permission_file_metadata_view,), text=_('File metadata'),
    view='file_metadata:document_driver_list',
)
link_document_file_metadata_list = Link(
    args=('resolved_object.id',), icon_class=icon_file_metadata,
    permissions=(permission_file_metadata_view,), text=_('Attributes'),
    view='file_metadata:document_version_driver_file_metadata_list',
)
link_document_submit = Link(
    args='resolved_object.id', permissions=(permission_file_metadata_submit,),
    text=_('Submit for file metadata'), view='file_metadata:document_submit'
)
link_document_submit_multiple = Link(
    text=_('Submit for file metadata'),
    view='file_metadata:document_submit_multiple'
)
link_document_type_file_metadata_settings = Link(
    args='resolved_object.id',
    icon_class=icon_file_metadata,
    permissions=(permission_document_type_file_metadata_setup,),
    text=_('Setup file metadata'),
    view='file_metadata:document_type_settings',
)

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.icons import icon_document_list
from mayan.apps.navigation import Link, get_cascade_condition

from .icons import (
    icon_document_multiple_tag_multiple_remove, icon_document_multiple_tag_multiple_remove,
    icon_document_tag_multiple_attach, icon_tag_create, icon_tag_delete, icon_tag_edit,
    icon_tag_document_list, icon_tag_list, icon_tag_multiple_delete,
    icon_document_tag_multiple_remove
)
from .permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)


link_document_tag_list = Link(
    args='resolved_object.pk', icon_class=icon_tag_document_list,
    permission=permission_tag_view, text=_('Tags'), view='tags:document_tags'
)
link_document_multiple_tag_multiple_attach = Link(
    icon_class=icon_document_multiple_tag_multiple_remove, text=_('Attach tags'),
    view='tags:document_multiple_tag_multiple_attach'
)
link_document_multiple_tag_multiple_remove = Link(
    icon_class=icon_document_multiple_tag_multiple_remove, text=_('Remove tag'),
    view='tags:document_multiple_tag_multiple_remove'
)
link_document_tag_multiple_attach = Link(
    args='object.pk', icon_class=icon_document_tag_multiple_attach,
    permission=permission_tag_attach, text=_('Attach tags'),
    view='tags:document_tag_multiple_attach'
)
link_document_tag_multiple_remove = Link(
    args='object.id', icon_class=icon_document_tag_multiple_remove,
    permission=permission_tag_remove, text=_('Remove tags'),
    view='tags:document_tag_multiple_remove'
)
link_tag_create = Link(
    icon_class=icon_tag_create, permission=permission_tag_create,
    text=_('Create new tag'), view='tags:tag_create'
)
link_tag_delete = Link(
    args='object.id', icon_class=icon_tag_delete,
    permission=permission_tag_delete, tags='dangerous', text=_('Delete'),
    view='tags:tag_delete'
)
link_tag_edit = Link(
    args='object.id', icon_class=icon_tag_edit,
    permission=permission_tag_edit, text=_('Edit'), view='tags:tag_edit'
)
link_tag_list = Link(
    condition=get_cascade_condition(
        app_label='tags', model_name='Tag',
        object_permission=permission_tag_view,
    ), icon_class=icon_tag_list, text=_('All'), view='tags:tag_list'
)
link_tag_multiple_delete = Link(
    icon_class=icon_tag_multiple_delete, permission=permission_tag_delete,
    text=_('Delete'), view='tags:tag_multiple_delete'
)
link_tag_tagged_item_list = Link(
    args='object.id', icon_class=icon_document_list, text=('Documents'),
    view='tags:tag_tagged_item_list'
)

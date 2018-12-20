from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Menu

from .icons import icon_menu_about, icon_menu_user

__all__ = (
    'menu_about', 'menu_facet', 'menu_list_facet', 'menu_main', 'menu_object',
    'menu_multi_item', 'menu_secondary', 'menu_setup', 'menu_sidebar',
    'menu_tools', 'menu_topbar', 'menu_user'
)

menu_about = Menu(
    icon_class=icon_menu_about, label=_('System'), name='about menu'
)
menu_facet = Menu(name='object facet')
menu_list_facet = Menu(name='object list facet')
menu_main = Menu(name='main menu')
menu_multi_item = Menu(name='multi item menu')
menu_object = Menu(name='object menu')
menu_secondary = Menu(name='secondary menu')
menu_setup = Menu(name='setup menu')
menu_sidebar = Menu(name='sidebar menu')
menu_tools = Menu(name='tools menu')
menu_topbar = Menu(name='menu topbar')
menu_user = Menu(
    icon_class=icon_menu_user, name='user menu', label=_('User')
)

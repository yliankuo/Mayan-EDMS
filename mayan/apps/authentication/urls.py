from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import logout

from .views import (
    login_view, password_change_done, password_change_view,
    password_reset_complete_view, password_reset_confirm_view,
    password_reset_done_view, password_reset_view
)

urlpatterns = [
    url(regex=r'^login/$', name='login_view', view=login_view),
    url(
        regex=r'^logout/$', kwargs={'next_page': settings.LOGIN_REDIRECT_URL},
        name='logout_view', view=logout
    ),
    url(
        regex=r'^password/change/$', name='password_change_view',
        view=password_change_view
    ),
    url(
        regex=r'^password/change/done/$', name='password_change_done',
        view=password_change_done
    ),
    url(
        regex=r'^password/reset/$', name='password_reset_view',
        view=password_reset_view
    ),
    url(
        regex=r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        name='password_reset_confirm_view', view=password_reset_confirm_view
    ),
    url(
        regex=r'^password/reset/complete/$',
        name='password_reset_complete_view', view=password_reset_complete_view
    ),
    url(
        regex=r'^password/reset/done/$', name='password_reset_done_view',
        view=password_reset_done_view
    ),
]

from __future__ import unicode_literals

#from rest_framework import routers

#router = routers.SimpleRouter()
#router.register(r'users', UserViewSet)
#router.register(r'accounts', AccountViewSet)
#urlpatterns = router.urls

#router = routers.DefaultRouter()
#from mayan.apps.rest_api.api_views import router
#from mayan.apps.rest_api.urls import router

from .api_views import TagViewSet

router_entries = (
    {'prefix': r'tags', 'viewset': TagViewSet, 'base_name': 'tag'},
)

#router.register(prefix=r'tags', viewset=TagViewSet, basename='tag')

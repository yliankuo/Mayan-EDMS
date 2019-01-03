from __future__ import absolute_import, unicode_literals

from rest_framework.test import APITestCase

from mayan.apps.acls.tests.mixins import ACLTestCaseMixin
from mayan.apps.common.tests.mixins import ClientMethodsTestCaseMixin
from mayan.apps.permissions.classes import Permission
from mayan.apps.smart_settings.classes import Namespace
from mayan.apps.user_management.tests.mixins import UserTestCaseMixin


class BaseAPITestCase(ClientMethodsTestCaseMixin, ACLTestCaseMixin, UserTestCaseMixin, APITestCase):
    """
    API test case class that invalidates permissions and smart settings
    """
    def setUp(self):
        super(BaseAPITestCase, self).setUp()
        Namespace.invalidate_cache_all()
        Permission.invalidate_cache()

    def tearDown(self):
        super(BaseAPITestCase, self).tearDown()

from uuid import uuid4

from oauth2_provider.models import AccessToken, Application, Grant, RefreshToken
from provider.oauth2.tests import BaseOAuth2TestCase
from student.tests.factories import UserFactory

from ..data_retirement_utils import (
    delete_from_oauth2_accesstoken,
    delete_from_oauth2_application,
    delete_from_oauth2_grant,
    delete_from_oauth2_refreshtoken,
    delete_from_oauth_consumer,
    delete_from_oauth_token,
)


class TestRetireUserFromOauth2AccessToken(BaseOAuth2TestCase):

    def setUp(self):
        super(TestRetireUserFromOauth2AccessToken, self).setUp()

    def test_delete_from_oauth2_accesstoken(self):
        user = self.get_user()
        client = self.get_client()
        token = AccessToken.objects.create(user=user, client=client)
        self.assertTrue(delete_from_oauth2_accesstoken(user))

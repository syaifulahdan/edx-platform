from django.test import TestCase

from ..data_retirement_utils import delete_oauth2_data_by_user_value

from student.tests.factories import UserFactory


class TestDataRetirementUtils(TestCase):

    def setUp(self):
        pass

    def test_delete_oauth2_data_returns_something(self):
        user = UserFactory.create()
        self.assertTrue(delete_oauth2_data_by_user_value(user))

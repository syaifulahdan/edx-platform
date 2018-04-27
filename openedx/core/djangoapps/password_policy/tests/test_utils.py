"""
Test password policy utilities
"""
from django.test import TestCase, override_settings

from mock import patch

from openedx.core.djangoapps.password_policy.constants import PASSWORD_POLICY_COMPLIANT_USERS_GROUP_NAME
from openedx.core.djangoapps.password_policy.utils import is_password_compliant, check_password_policy_compliance
from util.password_policy_validators import ValidationError
from student.tests.factories import UserFactory, GroupFactory


class Test(TestCase):
    def test_is_password_compliant(self):
        """
        Test the is compliant method returns false if a ValidationError is thrown, or true if anything else is returned
        """
        with patch('openedx.core.djangoapps.password_policy.utils.validate_password') as mock_validate_password:
            mock_validate_password.return_value = 'Any return value'
            self.assertTrue(is_password_compliant(None, 'somepassword'))

        with patch('openedx.core.djangoapps.password_policy.utils.validate_password') as mock_validate_password:
            mock_validate_password.side_effect = ValidationError('This is an error')
            self.assertFalse(is_password_compliant(None, 'somepassword'))

    @override_settings(PASSWORD_POLICY_COMPLIANCE_ROLLOUT_CONFIG={'ENABLE_COMPLIANCE_CHECKING': False})
    def test_check_password_policy_compliance_config_disabled(self):
        """
        Test that if the config is disabled or nonexistent nothing is returned
        """
        # Parameters don't matter for this method as it only tests the config
        self.assertIsNone(check_password_policy_compliance(None, None, None))

    @override_settings(PASSWORD_POLICY_COMPLIANCE_ROLLOUT_CONFIG={'ENABLE_COMPLIANCE_CHECKING': True})
    def test_check_password_policy_compliance(self):
        """
        Test that if the config is enabled:
            * Nothing is returned if the user is already in the PASSWORD_POLICY_COMPLIANT_USERS_GROUP_NAME
            * The user is added to the group if their password is found to be compliant
            * If there is no deadline return
        """
        user = UserFactory()
        group = GroupFactory.create(name=PASSWORD_POLICY_COMPLIANT_USERS_GROUP_NAME)
        user.groups.add(group)
        self.assertIsNone(check_password_policy_compliance(user, None, None))  # Do not need a password or request here

        with patch('openedx.core.djangoapps.password_policy.utils.validate_password') as mock_validate_password:
            user = UserFactory()
            # Make validate_password return True without checking the password
            mock_validate_password.return_value = True
            self.assertFalse(user.groups.all())  # Make sure there are no groups to start with
            self.assertIsNone(check_password_policy_compliance(user, None, None))
            # Make sure the user gets added to the group for having a compliant password
            self.assertTrue(user.groups.filter(name=PASSWORD_POLICY_COMPLIANT_USERS_GROUP_NAME).exists())

        with patch('openedx.core.djangoapps.password_policy.utils.validate_password') as mock_validate_password:
            mock_validate_password.side_effect = ValidationError('Some error message')
            with patch('openedx.core.djangoapps.password_policy.utils.get_enforcement_deadline_for_user') as \
                    mock_get_enforcement_deadline_for_user:
                user = UserFactory()
                # Make validate_password return True without checking the password
                mock_get_enforcement_deadline_for_user.return_value = None
                self.assertFalse(user.groups.all())  # Make sure there are no groups to start with
                self.assertIsNone(check_password_policy_compliance(user, None, None))
                self.assertFalse(user.groups.all())  # Make sure there are still groups

    def test_get_enforcement_deadline_for_user(self):
        pass

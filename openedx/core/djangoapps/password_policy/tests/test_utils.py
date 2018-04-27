"""
Test password policy utilities
"""
from django.test import TestCase, override_settings

from mock import patch

from openedx.core.djangoapps.password_policy.utils import is_password_compliant, check_password_policy_compliance
from util.password_policy_validators import ValidationError


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
    def test_check_password_policy_compliance_config(self):
        """
        Test that if the config is disabled or nonexistent nothing is returned
        """
        # Parameters don't matter for this method as it only tests the config
        self.assertIsNone(check_password_policy_compliance(None, None, None))

    def test_get_enforcement_deadline_for_user(self):
        pass

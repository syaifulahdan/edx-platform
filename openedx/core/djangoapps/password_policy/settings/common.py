def plugin_settings(settings):
    # Settings for managing the rollout of password policy compliance enforcement.
    settings.PASSWORD_POLICY_COMPLIANCE_ROLLOUT_CONFIG = {
        # Global switch to enable/disable password policy compliance checking on login.
        'ENABLE_COMPLIANCE_CHECKING': False,

        # The date that staff users (users with is_staff permissions) will be required to be compliant with
        # current password policy requirements. After this date, non-compliant users will be forced to reset their
        # password before logging in.
        #
        # This should be a timezone-aware date string parsable by dateutils.parser.parse
        # Ex: 2018-04-19 00:00:00+00:00
        'STAFF_USER_COMPLIANCE_DEADLINE': None,

        # The date that users with elevated privileges (users with entries in the course_access_roles table) will be
        # required to be compliant with current password policy requirements. After this date, non-compliant users will
        # be forced to reset their password before logging in.
        #
        # This should be a timezone-aware date string parsable by dateutils.parser.parse
        # Ex: 2018-04-19 00:00:00+00:00
        'ELEVATED_PRIVILEGE_USER_COMPLIANCE_DEADLINE': None,

        # The date that all users will be required to be compliant with current password policy requirements. After
        # this date, non-compliant users will be forced to reset their password before logging in.
        #
        # This should be a timezone-aware date string parsable by dateutils.parser.parse
        # Ex: 2018-04-19 00:00:00+00:00
        'GENERAL_USER_COMPLIANCE_DEADLINE': None,

        # The number of days before the compliance deadline that we will display a warning to non-compliant users that
        # they will be forced to reset their password.
        'DAYS_BEFORE_DEADLINE_TO_SHOW_WARNING': 30
    }

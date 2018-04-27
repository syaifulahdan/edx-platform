"""
Utilities for enforcing and tracking compliance with password policy rules.
"""
import pytz
from datetime import datetime
from dateutil.parser import parse as parse_date

from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _

from openedx.core.djangoapps.password_policy.constants import PASSWORD_POLICY_COMPLIANT_USERS_GROUP_NAME
from util.date_utils import strftime_localized, DEFAULT_SHORT_DATE_FORMAT
from util.password_policy_validators import validate_password


class NonCompliantPasswordException(Exception):
    """
    Exception that should be raised when a user who is required to be compliant with password policy requirements
    is found to have a non-compliant password.
    """
    pass


class NonCompliantPasswordWarning(Exception):
    """
    Exception that should be raised when a user who will soon be required to be compliant with password policy 
    requirements is found to have a non-compliant password.
    """
    pass


def should_enforce_compliance_on_login():
    """
    Returns a boolean indicating whether or not password policy compliance should be enforced on login.
    """
    config = _rollout_config()
    return config.get('ENFORCE_COMPLIANCE_ON_LOGIN', False)


def enforce_compliance_on_login(user, password):
    """
    Verify that the user's password is compliant with password policy rules and determine what should be done
    if it is not.

    Raises NonCompliantPasswordException when the password is found to be non-compliant and the compliance deadline
    for the user has been reached. In this case, login should be prevented.

    Raises NonCompliantPasswordWarning when the password is found to be non-compliant and the compliance deadline for
    the user is in the future.

    Returns None when the password is found to be compliant, or when no deadline for compliance has been set for the
    user.

    Important: This method should only be called AFTER the user has been authenticated.
    """
    is_compliant = _check_user_compliance(user, password)
    if is_compliant:
        return

    deadline = _get_compliance_deadline_for_user(user)
    if deadline is None:
        return

    now = datetime.now(pytz.UTC)
    if now >= deadline:
        raise NonCompliantPasswordException(
            _(
                '{platform_name} now requires more complex passwords. Your current password does not meet the new '
                'requirements. Change your password now to continue using the site. Thank you for helping us keep '
                'your data safe.'
            ).format(platform_name=settings.PLATFORM_NAME)
        )
    else:
        raise NonCompliantPasswordWarning(
            _(
                '{platform_name} now requires more complex passwords. Your current password does not meet the new '
                'requirements. You must change your password by {deadline} to be able to continue using the site. '
                'Thank you for helping us keep your data safe.'
            ).format(
                platform_name=settings.PLATFORM_NAME,
                deadline=strftime_localized(deadline, DEFAULT_SHORT_DATE_FORMAT)
            )
        )


def _rollout_config():
    """
    Return a dictionary with configuration settings for managing the rollout of password policy compliance
    enforcement.
    """
    return getattr(settings, 'PASSWORD_POLICY_COMPLIANCE_ROLLOUT_CONFIG', {})


def _check_user_compliance(user, password):
    """
    Returns a boolean indicating whether or not the user is compliant with password policy rules.

    A user is considered to be compliant if any of the following are true:
    - They are a member of the PASSWORD_POLICY_COMPLIANT_USERS_GROUP_NAME Group
    - The provided password argument meets current password policy requirements.

    In the event that a user that is not a member of the PASSWORD_POLICY_COMPLIANT_USERS_GROUP_NAME Group is found to
    be compliant, this method will attempt to add them to that Group before returning.
    """

    # Check if the user is a member of the compliant users group.
    try:
        if user.groups.filter(name=PASSWORD_POLICY_COMPLIANT_USERS_GROUP_NAME).exists():
            return True
    except:
        # If we fail to verify group membership, fallback to checking the password again.
        pass

    # Check if the user's password meets current policy requirements.
    try
        validate_password(password, user=user)
        is_compliant = True
    except:
        # If anything goes wrong, we should assume the password is not compliant but we don't necessarily
        # need to prevent login.
        is_compliant = False

    # If the password was confirmed to be compliant, add the user to compliant users group.
    if is_compliant:
        try:
            user.groups.add(Group.objects.get(name=PASSWORD_POLICY_COMPLIANT_USERS_GROUP_NAME))
        except:
            # Failing to add the user to the compliant users group is not a reason to prevent login.
            pass

    return is_compliant


def _get_compliance_deadline_for_user(user):
    """
    Returns the date that the user will be required to comply with password policy rules, or None if no such date
    applies to this user.
    """
    config = _rollout_config()

    staff_deadline = config.get('STAFF_USER_COMPLIANCE_DEADLINE', None)
    if staff_deadline:
        staff_deadline = parse_date(staff_deadline)

    elevated_privilege_user_deadline = config.get('ELEVATED_PRIVILEGE_USER_COMPLIANCE_DEADLINE', None)
    if elevated_privilege_user_deadline:
        elevated_privilege_user_deadline = parse_date(elevated_privilege_user_deadline)

    general_user_deadline = config.get('GENERAL_USER_COMPLIANCE_DEADLINE', None)
    if general_user_deadline:
        general_user_deadline = parse_date(general_user_deadline)

    if staff_deadline and user.is_staff:
        return staff_deadline
    elif elevated_privilege_user_deadline and user.courseaccessrole_set.exists():
        return elevated_privilege_user_deadline
    else:
        return general_user_deadline

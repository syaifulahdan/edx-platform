import pytz
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

from openedx.core.djangoapps.util.user_messages import PageLevelMessages, UserMessageType
from util.date_utils import strftime_localized, DEFAULT_SHORT_DATE_FORMAT
from util.password_policy_validators import ValidationError, validate_password


class NonCompliantPasswordException(Exception):
    pass


def check_password_policy_compliance(user, password, request=None):
    config = settings.PASSWORD_POLICY_COMPLIANCE_ROLLOUT_CONFIG
    if not (config and config.get('ENABLE_COMPLIANCE_CHECKING', False)):
        return

    is_compliant = is_password_compliant(user, password)
    if is_compliant:
        return

    deadline = get_enforcement_deadline_for_user(config, user)
    if deadline is None:
        return

    now = datetime.now(pytz.UTC)
    warning_days = config.get('DAYS_BEFORE_DEADLINE_TO_SHOW_WARNING', 0)

    if now >= deadline:
        raise NonCompliantPasswordException()
    elif request and warning_days and deadline - timedelta(days=warning_days) <= now:
        messages.add_message(
            request,
            UserMessageType.WARNING.value,
            _('Your password is not compliant with current policy requirements and will need to be updated on or '
              'before {deadline}').format(deadline=strftime_localized(deadline, DEFAULT_SHORT_DATE_FORMAT)),
            extra_tags=PageLevelMessages.get_namespace()
        )


def is_password_compliant(user, password):
    try:
        validate_password(password, user=user)
        return True
    except ValidationError:
        return False


def get_enforcement_deadline_for_user(rollout_config, user):
    staff_deadline = rollout_config.get('STAFF_USER_COMPLIANCE_DEADLINE', None)
    if staff_deadline:
        staff_deadline = parse_date(staff_deadline)

    elevated_privilege_user_deadline = rollout_config.get('ELEVATED_PRIVILEGE_USER_COMPLIANCE_DEADLINE', None)
    if elevated_privilege_user_deadline:
        elevated_privilege_user_deadline = parse_date(elevated_privilege_user_deadline)

    general_user_deadline = rollout_config.get('GENERAL_USER_COMPLIANCE_DEADLINE', None)
    if general_user_deadline:
        general_user_deadline = parse_date(general_user_deadline)

    if staff_deadline and user.is_staff:
        return staff_deadline
    elif elevated_privilege_user_deadline and user.courseaccessrole_set.count():
        return elevated_privilege_user_deadline
    else:
        return general_user_deadline

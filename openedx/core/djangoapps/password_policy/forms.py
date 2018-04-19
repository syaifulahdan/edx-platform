from django.contrib.admin.forms import AdminAuthenticationForm
from django.forms import ValidationError
from django.utils.translation import ugettext as _

from openedx.core.djangoapps.password_policy.utils import (
    NonCompliantPasswordException,
    check_password_policy_compliance
)


class PasswordPolicyAwareAdminAuthForm(AdminAuthenticationForm):
    def clean(self):
        cleaned_data = super(PasswordPolicyAwareAdminAuthForm, self).clean()

        try:
            check_password_policy_compliance(self.user_cache, cleaned_data['password'], self.request)
        except NonCompliantPasswordException:
            raise ValidationError(_(
                'Your password is not compliant with the current password policy. You must reset your password'
                ' before you can log in again.'
            ))

        return cleaned_data

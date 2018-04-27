"""
Defines the URL routes for this app.
"""

from django.conf import settings
from django.conf.urls import url

from ..profile_images.views import ProfileImageView
from .accounts.views import (
    AccountDeactivationView,
    AccountRetireMailingsView,
    AccountRetirementView,
    AccountViewSet,
    DeactivateLogoutView
)
from .preferences.views import PreferencesDetailView, PreferencesView
from .verification_api.views import IDVerificationStatusView
from .validation.views import RegistrationValidationView

ME = AccountViewSet.as_view({
    'get': 'get',
})

ACCOUNT_LIST = AccountViewSet.as_view({
    'get': 'list',
})

ACCOUNT_DETAIL = AccountViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
})

RETIREMENT_QUEUE = AccountRetirementView.as_view({
    'get': 'retirement_queue'
})

RETIREMENT_RETRIEVE = AccountRetirementView.as_view({
    'get': 'retrieve'
})

RETIREMENT_UPDATE = AccountRetirementView.as_view({
    'patch': 'partial_update',
})


urlpatterns = [
    url(
        r'^v1/me$',
        ME,
        name='own_username_api'
    ),
    url(
        r'^v1/accounts$',
        ACCOUNT_LIST,
        name='accounts_detail_api'
    ),
    url(
        r'^v1/accounts/{}$'.format(settings.USERNAME_PATTERN),
        ACCOUNT_DETAIL,
        name='accounts_api'
    ),
    url(
        r'^v1/accounts/{}/image$'.format(settings.USERNAME_PATTERN),
        ProfileImageView.as_view(),
        name='accounts_profile_image_api'
    ),
    url(
        r'^v1/accounts/{}/deactivate/$'.format(settings.USERNAME_PATTERN),
        AccountDeactivationView.as_view(),
        name='accounts_deactivation'
    ),
    url(
        r'^v1/accounts/retire_mailings/$',
        AccountRetireMailingsView.as_view(),
        name='accounts_retire_mailings'
    ),
    url(
        r'^v1/accounts/deactivate_logout/$',
        DeactivateLogoutView.as_view(),
        name='deactivate_logout'
    ),
    url(
        r'^v1/accounts/{}/verification_status/$'.format(settings.USERNAME_PATTERN),
        IDVerificationStatusView.as_view(),
        name='verification_status'
    ),
    url(
        r'^v1/accounts/{}/retirement_status/$'.format(settings.USERNAME_PATTERN),
        RETIREMENT_RETRIEVE,
        name='accounts_retirement_retrieve'
    ),
    url(
        r'^v1/accounts/retirement_queue/$',
        RETIREMENT_QUEUE,
        name='accounts_retirement_queue'
    ),
    url(
        r'^v1/accounts/update_retirement_status/$',
        RETIREMENT_UPDATE,
        name='accounts_retirement_update'
    ),
    url(
        r'^v1/validation/registration$',
        RegistrationValidationView.as_view(),
        name='registration_validation'
    ),
    url(
        r'^v1/preferences/{}$'.format(settings.USERNAME_PATTERN),
        PreferencesView.as_view(),
        name='preferences_api'
    ),
    url(
        r'^v1/preferences/{}/(?P<preference_key>[a-zA-Z0-9_]+)$'.format(settings.USERNAME_PATTERN),
        PreferencesDetailView.as_view(),
        name='preferences_detail_api'
    ),
]

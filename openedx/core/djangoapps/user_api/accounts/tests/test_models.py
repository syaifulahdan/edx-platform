"""
Model specific tests for user_api
"""
import pytest

from openedx.core.djangoapps.user_api.models import RetirementState, RetirementStateError, UserRetirementStatus
from student.models import get_retired_email_by_email, get_retired_username_by_username
from student.tests.factories import UserFactory


# Tell pytest it's ok to use the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_retirement_states():
    """
    Pytest fixture to create some basic states for testing. Duplicates functionality of the
    Django test runner in test_views.py unfortunately, but they're not compatible.
    """
    default_states = [
        ('PENDING', 1, False, True),
        ('LOCKING_ACCOUNT', 20, False, False),
        ('LOCKING_COMPLETE', 30, False, False),
        ('RETIRING_LMS', 40, False, False),
        ('LMS_COMPLETE', 50, False, False),
        ('ERRORED', 60, True, True),
        ('ABORTED', 70, True, True),
        ('COMPLETE', 80, True, True),
    ]

    for name, ex, dead, req in default_states:
        RetirementState.objects.create(
            state_name=name,
            state_execution_order=ex,
            is_dead_end_state=dead,
            required=req
        )


def _assert_retirementstatus_is_user(retirement, user):
    """
    Helper function to compare a newly created UserRetirementStatus object to expected values for
    the given user.
    """
    pending = RetirementState.objects.all().order_by('state_execution_order')[0]
    retired_username = get_retired_username_by_username(user.username)
    retired_email = get_retired_email_by_email(user.email)

    assert retirement.user == user
    assert retirement.original_username == user.username
    assert retirement.original_email == user.email
    assert retirement.original_name == user.profile.name
    assert retirement.retired_username == retired_username
    assert retirement.retired_email == retired_email
    assert retirement.current_state == pending
    assert retirement.last_state == pending
    assert pending.state_name in retirement.responses


def test_retirement_create_success(setup_retirement_states):  # pylint: disable=unused-argument, redefined-outer-name
    """
    Basic test to make sure default creation succeeds
    """
    user = UserFactory()
    retirement = UserRetirementStatus.create_retirement(user)
    _assert_retirementstatus_is_user(retirement, user)


def test_retirement_create_no_default_state():
    """
    Confirm that if no states have been loaded we fail with a RetirementStateError
    """
    user = UserFactory()

    with pytest.raises(RetirementStateError):
        UserRetirementStatus.create_retirement(user)


def test_retirement_create_already_retired(setup_retirement_states):  # pylint: disable=unused-argument, redefined-outer-name
    """
    Confirm the correct error bubbles up if the user already has a retirement row
    """
    user = UserFactory()
    retirement = UserRetirementStatus.create_retirement(user)
    _assert_retirementstatus_is_user(retirement, user)

    with pytest.raises(RetirementStateError):
        UserRetirementStatus.create_retirement(user)

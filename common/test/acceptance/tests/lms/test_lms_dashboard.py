# -*- coding: utf-8 -*-
"""
End-to-end tests for the main LMS Dashboard (aka, Student Dashboard).
"""
import datetime

from nose.plugins.attrib import attr

from common.test.acceptance.fixtures.course import CourseFixture
from common.test.acceptance.pages.common.auto_auth import AutoAuthPage
from common.test.acceptance.pages.lms.dashboard import DashboardPage
from common.test.acceptance.tests.helpers import UniqueCourseTest, generate_course_key

DEFAULT_SHORT_DATE_FORMAT = '{dt:%b} {dt.day}, {dt.year}'
TEST_DATE_FORMAT = '{dt:%b} {dt.day}, {dt.year} {dt.hour:02}:{dt.minute:02}'


class BaseLmsDashboardTest(UniqueCourseTest):
    """ Base test suite for the LMS Student Dashboard """

    def setUp(self):
        """
        Initializes the components (page objects, courses, users) for this test suite
        """
        # Some parameters are provided by the parent setUp() routine, such as the following:
        # self.course_id, self.course_info, self.unique_id
        super(BaseLmsDashboardTest, self).setUp()

        # Load page objects for use by the tests
        self.dashboard_page = DashboardPage(self.browser)

        # Configure some aspects of the test course and install the settings into the course
        self.course_fixture = CourseFixture(
            self.course_info["org"],
            self.course_info["number"],
            self.course_info["run"],
            self.course_info["display_name"],
        )
        self.course_fixture.add_advanced_settings({
            u"social_sharing_url": {u"value": "http://custom/course/url"}
        })
        self.course_fixture.install()

        self.username = "test_{uuid}".format(uuid=self.unique_id[0:6])
        self.email = "{user}@example.com".format(user=self.username)

        # Create the test user, register them for the course, and authenticate
        AutoAuthPage(
            self.browser,
            username=self.username,
            email=self.email,
            course_id=self.course_id
        ).visit()

        # Navigate the authenticated, enrolled user to the dashboard page and get testing!
        self.dashboard_page.visit()


class BaseLmsDashboardTestMultiple(UniqueCourseTest):
    """ Base test suite for the LMS Student Dashboard with Multiple Courses"""

    def setUp(self):
        """
        Initializes the components (page objects, courses, users) for this test suite
        """
        # Some parameters are provided by the parent setUp() routine, such as the following:
        # self.course_id, self.course_info, self.unique_id
        super(BaseLmsDashboardTestMultiple, self).setUp()

        # Load page objects for use by the tests
        self.dashboard_page = DashboardPage(self.browser)

        # Configure some aspects of the test course and install the settings into the course
        self.courses = {
            'A': {
                'org': 'test_org',
                'number': self.unique_id,
                'run': 'test_run_A',
                'display_name': 'Test Course A',
                'enrollment_mode': 'audit',
                'cert_name_long': 'Certificate of Audit Achievement'
            },
            'B': {
                'org': 'test_org',
                'number': self.unique_id,
                'run': 'test_run_B',
                'display_name': 'Test Course B',
                'enrollment_mode': 'verified',
                'cert_name_long': 'Certificate of Verified Achievement'
            },
            'C': {
                'org': 'test_org',
                'number': self.unique_id,
                'run': 'test_run_C',
                'display_name': 'Test Course C',
                'enrollment_mode': 'credit',
                'cert_name_long': 'Certificate of Credit Achievement'
            }
        }

        self.username = "test_{uuid}".format(uuid=self.unique_id[0:6])
        self.email = "{user}@example.com".format(user=self.username)

        self.course_keys = {}
        self.course_fixtures = {}

        for key, value in self.courses.iteritems():
            course_key = generate_course_key(
                value['org'],
                value['number'],
                value['run'],
            )

            course_fixture = CourseFixture(
                value['org'],
                value['number'],
                value['run'],
                value['display_name'],
            )

            course_fixture.add_advanced_settings({
                u"social_sharing_url": {u"value": "http://custom/course/url"},
                u"cert_name_long": {u"value": value['cert_name_long']}
            })

            course_fixture.install()

            self.course_keys[key] = course_key
            self.course_fixtures[key] = course_fixture

            # Create the test user, register them for the course, and authenticate
            AutoAuthPage(
                self.browser,
                username=self.username,
                email=self.email,
                course_id=course_key,
                enrollment_mode=value['enrollment_mode']
            ).visit()

        # Navigate the authenticated, enrolled user to the dashboard page and get testing!
        self.dashboard_page.visit()


@attr(shard=9)
class LmsDashboardPageTest(BaseLmsDashboardTest):
    """ Test suite for the LMS Student Dashboard page """

    def setUp(self):
        super(LmsDashboardPageTest, self).setUp()

        # now datetime for usage in tests
        self.now = datetime.datetime.now()

    def test_dashboard_course_listings(self):
        """
        Perform a general validation of the course listings section
        """
        course_listings = self.dashboard_page.get_course_listings()
        self.assertEqual(len(course_listings), 1)

    def test_dashboard_social_sharing_feature(self):
        """
        Validate the behavior of the social sharing feature
        """
        twitter_widget = self.dashboard_page.get_course_social_sharing_widget('twitter')
        twitter_url = ("https://twitter.com/intent/tweet?text=Testing+feature%3A%20http%3A%2F%2Fcustom%2Fcourse%2Furl"
                       "%3Futm_campaign%3Dsocial-sharing%26utm_medium%3Dsocial-post%26utm_source%3Dtwitter")
        self.assertEqual(twitter_widget.attrs('title')[0], 'Share on Twitter')
        self.assertEqual(twitter_widget.attrs('data-tooltip')[0], 'Share on Twitter')
        self.assertEqual(twitter_widget.attrs('target')[0], '_blank')
        self.assertIn(twitter_url, twitter_widget.attrs('href')[0])
        self.assertIn(twitter_url, twitter_widget.attrs('onclick')[0])

        facebook_widget = self.dashboard_page.get_course_social_sharing_widget('facebook')
        facebook_url = ("https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2Fcustom%2Fcourse%2Furl%3F"
                        "utm_campaign%3Dsocial-sharing%26utm_medium%3Dsocial-post%26utm_source%3Dfacebook&"
                        "quote=I%27m+taking+Test")
        self.assertEqual(facebook_widget.attrs('title')[0], 'Share on Facebook')
        self.assertEqual(facebook_widget.attrs('data-tooltip')[0], 'Share on Facebook')
        self.assertEqual(facebook_widget.attrs('target')[0], '_blank')
        self.assertIn(facebook_url, facebook_widget.attrs('href')[0])
        self.assertIn(facebook_url, facebook_widget.attrs('onclick')[0])

    def test_ended_course_date(self):
        """
        Scenario:
            Course Date should have the format 'Ended - Sep 23, 2015'
            if the course on student dashboard has ended.

        As a Student,
        Given that I have enrolled to a course
        And the course has ended in the past
        When I visit dashboard page
        Then the course date should have the following format "Ended - %b %d, %Y" e.g. "Ended - Sep 23, 2015"
        """
        course_start_date = datetime.datetime(1970, 1, 1)
        course_end_date = self.now - datetime.timedelta(days=90)

        self.course_fixture.add_course_details({
            'start_date': course_start_date,
            'end_date': course_end_date
        })
        self.course_fixture.configure_course()

        end_date = DEFAULT_SHORT_DATE_FORMAT.format(dt=course_end_date)
        expected_course_date = "Ended - {end_date}".format(end_date=end_date)

        # reload the page for changes to course date changes to appear in dashboard
        self.dashboard_page.visit()

        course_date = self.dashboard_page.get_course_date()

        # Test that proper course date with 'ended' message is displayed if a course has already ended
        self.assertEqual(course_date, expected_course_date)

    def test_running_course_date(self):
        """
        Scenario:
            Course Date should have the format 'Started - Sep 23, 2015'
            if the course on student dashboard is running.

        As a Student,
        Given that I have enrolled to a course
        And the course has started
        And the course is in progress
        When I visit dashboard page
        Then the course date should have the following format "Started - %b %d, %Y" e.g. "Started - Sep 23, 2015"
        """
        course_start_date = datetime.datetime(1970, 1, 1)
        course_end_date = self.now + datetime.timedelta(days=90)

        self.course_fixture.add_course_details({
            'start_date': course_start_date,
            'end_date': course_end_date
        })
        self.course_fixture.configure_course()

        start_date = DEFAULT_SHORT_DATE_FORMAT.format(dt=course_start_date)
        expected_course_date = "Started - {start_date}".format(start_date=start_date)

        # reload the page for changes to course date changes to appear in dashboard
        self.dashboard_page.visit()

        course_date = self.dashboard_page.get_course_date()

        # Test that proper course date with 'started' message is displayed if a course is in running state
        self.assertEqual(course_date, expected_course_date)

    def test_future_course_date(self):
        """
        Scenario:
            Course Date should have the format 'Starts - Sep 23, 2015'
            if the course on student dashboard starts in future.

        As a Student,
        Given that I have enrolled to a course
        And the course starts in future
        And the course does not start within 5 days
        When I visit dashboard page
        Then the course date should have the following format "Starts - %b %d, %Y" e.g. "Starts - Sep 23, 2015"
        """
        course_start_date = self.now + datetime.timedelta(days=30)
        course_end_date = self.now + datetime.timedelta(days=365)

        self.course_fixture.add_course_details({
            'start_date': course_start_date,
            'end_date': course_end_date
        })
        self.course_fixture.configure_course()

        start_date = DEFAULT_SHORT_DATE_FORMAT.format(dt=course_start_date)
        expected_course_date = "Starts - {start_date}".format(start_date=start_date)

        # reload the page for changes to course date changes to appear in dashboard
        self.dashboard_page.visit()

        course_date = self.dashboard_page.get_course_date()

        # Test that proper course date with 'starts' message is displayed if a course is about to start in future,
        # and course does not start within 5 days
        self.assertEqual(course_date, expected_course_date)

    def test_near_future_course_date(self):
        """
        Scenario:
            Course Date should have the format 'Starts - Wednesday at 5am UTC'
            if the course on student dashboard starts within 5 days.

        As a Student,
        Given that I have enrolled to a course
        And the course starts within 5 days
        When I visit dashboard page
        Then the course date should have the following format "Starts - %A at %-I%P UTC"
            e.g. "Starts - Wednesday at 5am UTC"
        """
        course_start_date = self.now + datetime.timedelta(days=2)
        course_end_date = self.now + datetime.timedelta(days=365)

        self.course_fixture.add_course_details({
            'start_date': course_start_date,
            'end_date': course_end_date
        })
        self.course_fixture.configure_course()

        start_date = TEST_DATE_FORMAT.format(dt=course_start_date)
        expected_course_date = "Starts - {start_date} UTC".format(start_date=start_date)

        # reload the page for changes to course date changes to appear in dashboard
        self.dashboard_page.visit()

        course_date = self.dashboard_page.get_course_date()

        # Test that proper course date with 'starts' message is displayed if a course is about to start in future,
        # and course starts within 5 days
        self.assertEqual(course_date, expected_course_date)

    def test_advertised_start_date(self):

        """
        Scenario:
            Course Date should be advertised start date
            if the course on student dashboard has `Course Advertised Start` set.

        As a Student,
        Given that I have enrolled to a course
        And the course has `Course Advertised Start` set.
        When I visit dashboard page
        Then the advertised start date should be displayed rather course start date"
        """
        course_start_date = self.now + datetime.timedelta(days=2)
        course_advertised_start = "Winter 2018"

        self.course_fixture.add_course_details({
            'start_date': course_start_date,
        })
        self.course_fixture.configure_course()

        self.course_fixture.add_advanced_settings({
            u"advertised_start": {u"value": course_advertised_start}
        })
        self.course_fixture._add_advanced_settings()

        expected_course_date = "Starts - {start_date}".format(start_date=course_advertised_start)

        self.dashboard_page.visit()
        course_date = self.dashboard_page.get_course_date()

        self.assertEqual(course_date, expected_course_date)

    def test_profile_img_alt_empty(self):
        """
        Validate value of profile image alt attribue is null
        """
        profile_img = self.dashboard_page.get_profile_img()
        self.assertEqual(profile_img.attrs('alt')[0], '')


class LmsDashboardCourseUnEnrollDialogMessageTest(BaseLmsDashboardTestMultiple):
    """
        Class to test lms student dashboard unenroll dialog messages.
    """

    def test_audit_course_run_unenroll_dialog_msg(self):
        """
        Validate unenroll dialog message when user clicks unenroll button for a audit course
        """

        self.dashboard_page.visit()
        dialog_message = self.dashboard_page.view_course_unenroll_dialog_message(str(self.course_keys['A']))
        course_number = self.courses['A']['number']
        course_name = self.courses['A']['display_name']

        expected_track_message = u'Are you sure you want to unenroll from' + \
                                 u' <span id="unenroll_course_name">' + course_name + u'</span>' + \
                                 u' (<span id="unenroll_course_number">' + course_number + u'</span>)?'

        self.assertEqual(dialog_message['track-info'][0], expected_track_message)

    def test_verified_course_run_unenroll_dialog_msg(self):
        """
        Validate unenroll dialog message when user clicks unenroll button for a verified course passed refund
        deadline
        """

        self.dashboard_page.visit()
        dialog_message = self.dashboard_page.view_course_unenroll_dialog_message(str(self.course_keys['B']))
        course_number = self.courses['B']['number']
        course_name = self.courses['B']['display_name']
        cert_long_name = self.courses['B']['cert_name_long']

        expected_track_message = u'Are you sure you want to unenroll from the verified' + \
                                 u' <span id="unenroll_cert_name">' + cert_long_name + u'</span>' + \
                                 u' track of <span id="unenroll_course_name">' + course_name + u'</span>' +  \
                                 u' (<span id="unenroll_course_number">' + course_number + u'</span>)?'

        expected_refund_message = u'The refund deadline for this course has passed,so you will not receive a refund.'

        self.assertEqual(dialog_message['track-info'][0], expected_track_message)
        self.assertEqual(dialog_message['refund-info'][0], expected_refund_message)


@attr('a11y')
class LmsDashboardA11yTest(BaseLmsDashboardTestMultiple):
    """
    Class to test lms student dashboard accessibility.
    """

    def test_dashboard_course_listings_a11y(self):
        """
        Test the accessibility of the course listings
        """
        course_listings = self.dashboard_page.get_courses()
        self.assertEqual(len(course_listings), 3)
        self.dashboard_page.a11y_audit.check_for_accessibility_errors()


class LmsDashboardCourseEntitlementTest(BaseLmsDashboardTest):
    """ Test suite for course entitlements cards on the Student Dashboard page """

    def test_unfulfilled_entitlement_card(self):
        """ Verify that a course card appears the learner's unfulfilled entitlement."""
        

    def test_unfulfilled_select_session_button(self):
        """
        Verify that a Select Session button is present and enabled on the unfulfilled entitlement's course card.
        """


    def test_select_session_popup(self):
        """ Verify that the 'Are you sure?' pop-up appears when the Select Session button is clicked."""


    def test_session_selected(self):
        """
        Verify that clicking 'OK' in the session selection pop-up removes the Select Session button
        from the course card and adds a View Course button and a 'Change or Leave Session' link.
        """


    def test_view_course_link(self):
        """ Verify that the the View Course button links to the course home for the proper course run."""


    def test_change_or_leave_session(self):
        """ Verify that clicking the 'Change or Leave Session' link shows the course run dropdown menu."""


    def test_change_session_no_selection(self):
        """ Verify that the 'Change Session' button is disabled before a new session or the leave option is selected."""


    def test_change_session_selection_made(self):
        """ Verify that the 'Change Session' button is enabled once a selection is made."""


    def test_new_session_view_course(self):
        """
        Verify that, when a user switches sessions, the 'View Course' button links to the new session's course home.
        """


    def test_leave_current_session(self):
        """
        Verify that selecting 'Leave the current session and decide later' changes the 'Change Session'
        button text to 'Leave Current Session'.
        """


    def test_leave_session_popup(self):
        """ Verify that clicking the 'Leave Current Session' button opens the 'Are you sure?' popup."""


    def test_remove_view_course(self):
        """ Verify that the View Course button is removed from the course card after leaving the current session."""


    def test_refundable_can_unenroll(self):
        """ Verify that the gear icon and unenroll option are available for an entitlement that is refundable."""


    def test_entitlement_unenrollment_modal(self):
        """
        Verify that selecting unenroll from the gear dropdown opens an entitlement unenrollment modal
        with the correct header for the course.
        """


    def test_entitlement_unenrollment_request(self):
        """
        Verify that selecting unenroll in the entitlement unenrollment modal triggers a DELETE request
        to the appropriate API endpoint to revoke/refund the entitlement and redirects the user to the dashboard.
        """


    def test_unrefundable_cannot_unenroll(self):
        """ Verify that the gear icon is not on the course card for an entitlement that is not refundable."""


    def test_logged_out_unenroll(self):
        """ Verify that a logged out user that selects unenroll is redirected to the login page."""


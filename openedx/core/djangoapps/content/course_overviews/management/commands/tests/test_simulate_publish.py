"""
Tests the simulate_publish management command.
"""
from StringIO import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.dispatch.dispatcher import receiver
from mock import patch

from openedx.core.djangoapps.content.course_overviews.management.commands import simulate_publish
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.content.course_overviews.signals import _listen_for_course_publish
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import SignalHandler
from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory


class TestSimulatePublish(SharedModuleStoreTestCase):

    @classmethod
    def setUpClass(cls):
        """
        Create courses in modulestore.

        Modulestore signals are suppressed by ModuleStoreIsolationMixin, so this
        method should not trigger things like CourseOverview creation. That
        means every test function
        """
        super(TestSimulatePublish, cls).setUpClass()
        cls.command = simulate_publish.Command()
        # org.0/course_0/Run_0
        cls.course_key_1 = CourseFactory.create(default_store=ModuleStoreEnum.Type.mongo).id
        # course-v1:org.1+course_1+Run_1
        cls.course_key_2 = CourseFactory.create(default_store=ModuleStoreEnum.Type.split).id
        # course-v1:org.2+course_2+Run_2
        cls.course_key_3 = CourseFactory.create(default_store=ModuleStoreEnum.Type.split).id

        # We want to enable the signal only after the courses have been created.
        cls.enable_signals_by_name('course_published')

    def setUp(self):
        super(TestSimulatePublish, self).setUp()
        SignalHandler.course_published.connect(self.sample_receiver_1)
        SignalHandler.course_published.connect(self.sample_receiver_2)
        self.received_1 = []
        self.received_2 = []

    def tearDown(self):
        SignalHandler.course_published.disconnect(self.sample_receiver_1)
        SignalHandler.course_published.disconnect(self.sample_receiver_2)
        super(TestSimulatePublish, self).tearDown()

    def options(self, **kwargs):
        """
        Return an options dict that can be passed to self.command.handle()

        Passed in **kwargs will override existing defaults. Most defaults are
        the same as they are for running the management command manually (e.g.
        dry_run is False, show_receivers is False), except that the list of
        receivers is by default limited to the two that exist in this test
        class. We do this to keep these tests faster and more self contained.
        """
        default_receivers = [
            simulate_publish.name_from_fn(self.sample_receiver_1),
            simulate_publish.name_from_fn(self.sample_receiver_2),
        ]
        default_options = dict(
            show_receivers=False,
            dry_run=False,
            receivers=default_receivers,
            courses=None,
            delay=0
        )
        default_options.update(kwargs)
        return default_options

    def test_specific_courses(self):
        """Test sending only to specific courses."""
        self.command.handle(
            **self.options(
                courses=[unicode(self.course_key_1), unicode(self.course_key_2)]
            )
        )
        self.assertIn(self.course_key_1, self.received_1)
        self.assertIn(self.course_key_2, self.received_1)
        self.assertNotIn(self.course_key_3, self.received_1)
        self.assertEqual(self.received_1, self.received_2)

    def test_specific_receivers(self):
        """Test sending only to specific receivers."""
        self.command.handle(
            **self.options(
                receivers=[simulate_publish.name_from_fn(self.sample_receiver_1)]
            )
        )
        self.assertIn(self.course_key_1, self.received_1)
        self.assertIn(self.course_key_2, self.received_1)
        self.assertIn(self.course_key_3, self.received_1)
        self.assertEqual(self.received_2, [])

    def test_course_overviews(self):
        """Integration test with CourseOverviews."""
        self.assertEqual(CourseOverview.objects.all().count(), 0)
        self.command.handle(
            **self.options(
                receivers=[simulate_publish.name_from_fn(_listen_for_course_publish)]
            )
        )
        self.assertEqual(CourseOverview.objects.all().count(), 3)
        self.assertEqual(self.received_1, [])
        self.assertEqual(self.received_2, [])

    def sample_receiver_1(self, sender, course_key, **kwargs):  # pylint: disable=unused-argument
        """Custom receiver for testing."""
        self.received_1.append(course_key)

    def sample_receiver_2(self, sender, course_key, **kwargs):  # pylint: disable=unused-argument
        """Custom receiver for testing."""
        self.received_2.append(course_key)

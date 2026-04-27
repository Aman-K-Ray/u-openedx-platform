"""
Exam Settings View Tests
"""
import ddt
import lxml
from django.conf import settings
from django.test.utils import override_settings
from edx_toggles.toggles.testutils import override_waffle_flag

from cms.djangoapps.contentstore import toggles
from cms.djangoapps.contentstore.tests.utils import CourseTestCase
from cms.djangoapps.contentstore.utils import reverse_course_url
from common.djangoapps.util.testing import UrlResetMixin


@ddt.ddt
@override_settings(
    FEATURES={
        **settings.FEATURES,
        "CERTIFICATES_HTML_VIEW": True,
        "ENABLE_PROCTORED_EXAMS": True,
    },
)
@override_waffle_flag(toggles.LEGACY_STUDIO_CERTIFICATES, True)
@override_waffle_flag(toggles.LEGACY_STUDIO_SCHEDULE_DETAILS, True)
@override_waffle_flag(toggles.LEGACY_STUDIO_CONFIGURATIONS, True)
@override_waffle_flag(toggles.LEGACY_STUDIO_GRADING, True)
@override_waffle_flag(toggles.LEGACY_STUDIO_ADVANCED_SETTINGS, True)
class TestExamSettingsView(CourseTestCase, UrlResetMixin):
    """
    Unit tests for the exam settings view.
    """
    def setUp(self):
        """
        Set up the for the exam settings view tests.
        """
        super().setUp()
        self.reset_urls()

    @staticmethod
    def _get_exam_settings_alert_text(raw_html_content):
        """ Get text content of alert banner """
        parsed_html = lxml.html.fromstring(raw_html_content)
        alert_nodes = parsed_html.find_class('exam-settings-alert')
        assert len(alert_nodes) == 1
        alert_node = alert_nodes[0]
        return alert_node.text_content()

    @override_waffle_flag(toggles.LEGACY_STUDIO_EXAM_SETTINGS, True)
    @ddt.data(
        "certificates_list_handler",
        "settings_handler",
        "group_configurations_list_handler",
        "grading_handler",
    )
    def test_view_without_exam_settings_enabled(self, handler):
        """
        Tests pages should not have `Exam Settings` item
        if course does not have the Exam Settings view enabled.
        """
        outline_url = reverse_course_url(handler, self.course.id)
        resp = self.client.get(outline_url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 200)  # noqa: PT009
        self.assertNotContains(resp, 'Proctored Exam Settings')

    @ddt.data(
        "certificates_list_handler",
        "settings_handler",
        "group_configurations_list_handler",
        "grading_handler",
    )
    def test_view_with_exam_settings_enabled(self, handler):
        """
        Tests pages should have `Exam Settings` item
        if course does have Exam Settings view enabled.
        """
        outline_url = reverse_course_url(handler, self.course.id)
        resp = self.client.get(outline_url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 200)  # noqa: PT009
        self.assertContains(resp, 'Proctored Exam Settings')

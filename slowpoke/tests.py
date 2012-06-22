import time

from django.conf import settings
from django.test import TestCase

from slowpoke.decorator import time_my_test
from slowpoke.models import *


class SlowPokeDecoratorTests(TestCase):

    @time_my_test('setup')
    def setUp(self):
        self._old_time_standards = getattr(settings, 'TIME_STANDARDS', False)
        settings.TIME_STANDARDS = False  # we want the defaults to take effect for these or else tests will have inconsistent results
        time.sleep(0.2)

    @time_my_test('teardown')
    def tearDown(self):
        settings.TIME_STANDARDS = self._old_time_standards
        time.sleep(0.1)

    @time_my_test('task')
    def test_task_ok(self):
        time.sleep(0.9)
        self.assertEqual(True, True)

    @time_my_test('task')
    def test_task_slow(self):
        time.sleep(1.1)
        self.assertEqual(True, True)

    @time_my_test('web_view')
    def test_view_ok(self):
        time.sleep(0.2)
        self.assertEqual(True, True)

    @time_my_test('web_view')
    def test_view_slow(self):
        time.sleep(0.35)
        self.assertEqual(True, True)

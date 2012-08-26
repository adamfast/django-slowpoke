import datetime
import socket
import time

from django.db import connections
from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner
try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.datetime.now

from slowpoke.models import *


class SlowPokeTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self, **kwargs):
        self.slowpoke_db_original = settings.DATABASES['slowpokelogs']['NAME']
        result = super(SlowPokeTestRunner, self).setup_databases(**kwargs)
        self.slowpoke_db_test = settings.DATABASES['slowpokelogs']['NAME']
        # set it back, we don't want to use an auto-destroyed test DB
        settings.DATABASES['slowpokelogs']['NAME'] = self.slowpoke_db_original
        connections['slowpokelogs'].close()  # the wrong connection is open right now. close it and Django will do the right thing next.
        # now create the run in the real database
        self._the_run.save(using='slowpokelogs')
        settings.CURRENT_SLOWPOKE_RUN = self._the_run.pk
        self._the_run = TestSuiteRun.objects.get(pk=self._the_run.pk)
        settings.CURRENT_SLOWPOKE_TEST_RUNS = []
        return result

    def teardown_databases(self, old_config, **kwargs):
        # set it back, we don't want to auto-destroy our real DB
        settings.DATABASES['slowpokelogs']['NAME'] = self.slowpoke_db_test
        result = super(SlowPokeTestRunner, self).teardown_databases(old_config, **kwargs)
        return result

    def build_suite(self, *args, **kwargs):
        suite = super(SlowPokeTestRunner, self).build_suite(*args, **kwargs)

        if getattr(settings, 'AVOID_TESTS_FOR', -1) != -1:
            keep_tests = []
            for case in suite:
                pkg = case.__class__.__module__.split('.')[0]
                if pkg not in settings.AVOID_TESTS_FOR:
                    keep_tests.append(case)

            suite._tests = keep_tests

        return suite

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        if getattr(settings, 'SOUTH_TESTS_MIGRATE', False) == True:
            print('settings.SOUTH_TESTS_MIGRATE is True, which will take longer as it migrates your database step by step.')

        if getattr(settings, 'SKIP_SOUTH_TESTS', False) == False:
            print('settings.SKIP_SOUTH_TESTS is False, which will take longer as South runs its own internal tests.')

        if getattr(settings, 'AVOID_TESTS_FOR', -1) == -1:
            print("If you want faster tests and aren't worried about running a bunch of Django's own tests, you can add AVOID_TESTS_FOR = ['django'] to your settings file to have them skipped. Any other apps you wish to skip can be added there as well.")

        self._the_run = TestSuiteRun(start=now(), machine=socket.gethostname())

        result = super(SlowPokeTestRunner, self).run_tests(test_labels, extra_tests, **kwargs)
        # this will call setup_databases(), do things, then teardown_databases.

        settings.DATABASES['slowpokelogs']['NAME'] = self.slowpoke_db_original
        self._the_run.end = now()
        self._the_run.save(using='slowpokelogs')

        for tr in settings.CURRENT_SLOWPOKE_TEST_RUNS:
            tr.suite_run = self._the_run
            tr.save(using='slowpokelogs')

        print('%d tests met their performance standard.' % self._the_run.testrun_set.filter(meets_standard=True).count())
        print('%d tests did not meet their performance standard.' % self._the_run.testrun_set.filter(meets_standard=False).count())

        for the_test in self._the_run.testrun_set.filter(meets_standard=False):
            print('%s took %sms, %sms allowed.' % (the_test.function_name, the_test.runtime_ms, TIME_STANDARDS.get(the_test.test_standard)))

        settings.DATABASES['slowpokelogs']['NAME'] = self.slowpoke_db_test
        return result

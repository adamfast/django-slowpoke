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
        result = super(SlowPokeTestRunner, self).setup_databases(**kwargs)
        # set it back, we don't want to use an auto-destroyed test DB
        settings.DATABASES['slowpokelogs']['NAME'] = 'slowpokelogs'
        connections['slowpokelogs'].close()  # the wrong connection is open right now. close it and Django will do the right thing next.
        # now create the run in the real database
        self._the_run.save(using='slowpokelogs')
        settings.CURRENT_SLOWPOKE_RUN = self._the_run.pk
        self._the_run = TestSuiteRun.objects.get(pk=self._the_run.pk)
        settings.CURRENT_SLOWPOKE_TEST_RUNS = []
        return result

    def teardown_databases(self, old_config, **kwargs):
        # set it back, we don't want to auto-destroy our real DB
        settings.DATABASES['slowpokelogs']['NAME'] = 'test_slowpokelogs'
        result = super(SlowPokeTestRunner, self).teardown_databases(old_config, **kwargs)
        return result

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        self._the_run = TestSuiteRun(start=now(), machine=socket.gethostname())

        result = super(SlowPokeTestRunner, self).run_tests(test_labels, extra_tests, **kwargs)
        # this will call setup_databases(), do things, then teardown_databases.

        settings.DATABASES['slowpokelogs']['NAME'] = 'slowpokelogs'
        self._the_run.end = now()
        self._the_run.save(using='slowpokelogs')

        for tr in settings.CURRENT_SLOWPOKE_TEST_RUNS:
            tr.suite_run = self._the_run
            tr.save(using='slowpokelogs')
        settings.DATABASES['slowpokelogs']['NAME'] = 'test_slowpokelogs'
        return result

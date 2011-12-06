import datetime
import time

from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

from slowpoke.models import *


class SlowPokeTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self, **kwargs):
        result = super(SlowPokeTestRunner, self).setup_databases(**kwargs)

        settings.DATABASES['slowpokelogs']['NAME'] = 'slowpokelogs'  # set it back, we don't want to use an auto-destroyed test DB

        return result

    def teardown_databases(self, old_config, **kwargs):
        settings.DATABASES['slowpokelogs']['NAME'] = 'test_slowpokelogs'  # set it back, we don't want to auto-destroyed our real DB

        result = super(SlowPokeTestRunner, self).teardown_databases(old_config, **kwargs)
        return result

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        the_run = TestSuiteRun.objects.using('slowpokelogs').create(start=datetime.datetime.now())
        settings.CURRENT_SLOWPOKE_RUN = the_run.pk

        result = super(SlowPokeTestRunner, self).run_tests(test_labels, extra_tests, **kwargs)

        the_run.end = datetime.datetime.now()
        the_run.save()

        return result

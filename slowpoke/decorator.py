# modified from http://www.zopyx.com/blog/a-python-decorator-for-measuring-the-execution-time-of-methods
import time

from django.conf import settings

from slowpoke.models import *


class time_my_test(object):

    def __init__(self, standard, *args, **kwargs):
        settings.CURRENT_SLOWPOKE_STANDARD = standard

    def __call__(self, func):

        def to_time(*args, **kwargs):
            ts = time.time()
            result = func(*args, **kwargs)
            te = time.time()

            # check this against TIME_STANDARDS for the level of function. Log if it was too slow.
            sr = TestSuiteRun.objects.using('slowpokelogs').get(pk=settings.CURRENT_SLOWPOKE_RUN)
            tr = TestRun()
            tr.suite_run = sr
            tr.test_standard = settings.CURRENT_SLOWPOKE_STANDARD
            tr.function_name = str(func.__name__)
            tr.args = str(args)
            tr.kwargs = str(kwargs)
            tr.runtime_ms = (te - ts) * 1000
            tr.save(using='slowpokelogs')
            return result
        return to_time

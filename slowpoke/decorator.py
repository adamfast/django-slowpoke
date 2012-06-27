# modified from http://www.zopyx.com/blog/a-python-decorator-for-measuring-the-execution-time-of-methods
import time

from django.conf import settings

from slowpoke.models import *


class time_my_test(object):

    def __init__(self, standard='unknown', *args, **kwargs):
        self.CURRENT_SLOWPOKE_STANDARD = standard

    def __call__(self, func):

        def to_time(*args, **kwargs):
            ts = time.time()
            result = func(*args, **kwargs)
            te = time.time()

            # Log this test's runtime.
            tr = TestRun()
            tr.test_standard = self.CURRENT_SLOWPOKE_STANDARD
            tr.function_name = str(func.__name__)
            tr.args = str(args)
            tr.kwargs = str(kwargs)
            tr.runtime_ms = (te - ts) * 1000
            settings.CURRENT_SLOWPOKE_TEST_RUNS.append(tr)
            return result
        return to_time

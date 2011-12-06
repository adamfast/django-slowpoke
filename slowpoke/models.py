from django.conf import settings
from django.db import models

TIME_STANDARDS = getattr(settings, 'TIME_STANDARDS', {
    'task': 1000,
    'web_view': 300,
})


class TestSuiteRun(models.Model):
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)


class TestRun(models.Model):
    suite_run = models.ForeignKey(TestSuiteRun)
    test_standard = models.CharField(max_length=128)
    function_name = models.CharField(max_length=512)
    args = models.TextField(null=True, blank=True)
    kwargs = models.TextField(null=True, blank=True)
    runtime_ms = models.PositiveIntegerField()

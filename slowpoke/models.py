from django.conf import settings
from django.db import models

TIME_STANDARDS = getattr(settings, 'TIME_STANDARDS', {
    'task': 1000,
    'web_view': 300,
})


class TestSuiteRun(models.Model):
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    machine = models.CharField(max_length=128)


class TestRun(models.Model):
    suite_run = models.ForeignKey(TestSuiteRun)
    test_standard = models.CharField(max_length=128)
    function_name = models.CharField(max_length=512)
    args = models.TextField(null=True, blank=True)
    kwargs = models.TextField(null=True, blank=True)
    runtime_ms = models.PositiveIntegerField()
    meets_standard = models.NullBooleanField()

    def test_standard_display(self):
        for standard in TIME_STANDARDS.keys():
            if str(standard) == str(self.test_standard):
                return u'%s (%s ms)' % (standard, TIME_STANDARDS[standard])
        return '?'


def populate_meets_standard(*args, **kwargs):
    instance = kwargs['instance']

    if instance.runtime_ms and TIME_STANDARDS.get(instance.test_standard, False):
        if instance.runtime_ms < TIME_STANDARDS[instance.test_standard]:
            instance.meets_standard = True
        else:
            instance.meets_standard = False
    else:
        instance.meets_standard = None
models.signals.pre_save.connect(populate_meets_standard, sender=TestRun)

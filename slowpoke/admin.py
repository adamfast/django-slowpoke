from django.contrib import admin

from slowpoke.models import *


class MultiDBModelAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.
    using = 'slowpokelogs'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super(MultiDBModelAdmin, self).queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request=request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request=request, using=self.using, **kwargs)


class TestRunInline(admin.TabularInline):
    using = 'slowpokelogs'
    model = TestRun
    fields = ('meets_standard', 'test_standard_display', 'runtime_ms', 'function_name', 'args', 'kwargs')
    readonly_fields = ('meets_standard', 'test_standard_display', 'test_standard', 'runtime_ms', 'function_name', 'args', 'kwargs')
    extra = 0

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super(TestRunInline, self).queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super(TestRunInline, self).formfield_for_foreignkey(db_field, request=request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super(TestRunInline, self).formfield_for_manytomany(db_field, request=request, using=self.using, **kwargs)


class TestSuiteRunAdmin(MultiDBModelAdmin):
    list_display = ('runtime', 'start', 'end', 'machine')
    list_filter = ('machine',)
    inlines = [TestRunInline,]
    readonly_fields = ('start', 'end', 'runtime', 'machine')


admin.site.register(TestSuiteRun, TestSuiteRunAdmin)
#admin.site.register(TestRun, TestRunAdmin)

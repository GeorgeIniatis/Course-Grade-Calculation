from django.contrib import admin
from chemapp.models import *
from django.contrib.auth.models import Permission


class SlugAdmin(admin.ModelAdmin):
    exclude = ('slug',)


admin.site.register(Student)
admin.site.register(Permission)
admin.site.register(Staff)
admin.site.register(Degree)
admin.site.register(Course, SlugAdmin)
admin.site.register(CourseGrade)
admin.site.register(Assessment, SlugAdmin)
admin.site.register(AssessmentGrade)
admin.site.register(AssessmentComponent)
admin.site.register(AssessmentComponentGrade)

# Register your models here.

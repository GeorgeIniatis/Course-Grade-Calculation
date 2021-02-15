from django.contrib import admin
from chemapp.models import *


class SlugAdmin(admin.ModelAdmin):
    exclude = ('slug',)


admin.site.register(UserProfile)
admin.site.register(Student)
admin.site.register(Degree)
admin.site.register(Course, SlugAdmin)
admin.site.register(CourseGrade)
admin.site.register(Assessment, SlugAdmin)
admin.site.register(AssessmentGrade)
admin.site.register(AssessmentComponent)
admin.site.register(AssessmentComponentGrade)

# Register your models here.

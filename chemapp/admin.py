from django.contrib import admin
from chemapp.models import *

class CourseAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    
admin.site.register(UserProfile)
admin.site.register(Student)
admin.site.register(Degree)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseGrade)
admin.site.register(Assessment)
admin.site.register(AssessmentGrade)
admin.site.register(AssessmentComponent)
admin.site.register(AssessmentComponentGrade)

# Register your models here.

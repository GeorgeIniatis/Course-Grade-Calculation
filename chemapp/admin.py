from django.contrib import admin
from chemapp.models import *
from django.contrib.auth.models import Permission
from import_export import resources
from .models import CourseGrade
from import_export.admin import ImportExportModelAdmin

# Before deployment remove access to Student/Staff/Degree/Course/CourseGrade/
# Assessment/AssessmentGrade/AssessmentComponent/AssessmentComponentGrade


class SlugAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    
    
    

class CGradeAdmin(ImportExportModelAdmin):
    pass
    
    
admin.site.register(Student)
admin.site.register(Permission)
admin.site.register(Staff)
admin.site.register(Degree)
admin.site.register(Course, SlugAdmin)
admin.site.register(CourseGrade,CGradeAdmin)
admin.site.register(Assessment, SlugAdmin)
admin.site.register(AssessmentGrade)
admin.site.register(AssessmentComponent)
admin.site.register(AssessmentComponentGrade)

# Register your models here.

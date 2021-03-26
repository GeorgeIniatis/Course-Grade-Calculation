from django.contrib import admin
from chemapp.models import *
from django.contrib.auth.models import Permission
from import_export import resources
from .models import CourseGrade





admin.site.register(Student)
admin.site.register(Permission)
admin.site.register(Staff)
admin.site.register(Degree)
admin.site.register(Course)
admin.site.register(CourseGrade)
admin.site.register(Assessment)
admin.site.register(AssessmentGrade)
admin.site.register(AssessmentComponent)
admin.site.register(AssessmentComponentGrade)

# Register your models here.

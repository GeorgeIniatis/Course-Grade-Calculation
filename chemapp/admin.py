from django.contrib import admin
from chemapp.models import *

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(UserProfile)
admin.site.register(Page)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(CourseGrade)
admin.site.register(Assessment)
admin.site.register(AssessmentGrade)

# Register your models here.

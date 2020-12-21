from django.contrib import admin
from chemapp.models import UserProfile,Category,Page ,Student,Course

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(UserProfile)
admin.site.register(Page)
admin.site.register(Student)
admin.site.register(Course)
# Register your models here.

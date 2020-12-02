from django.contrib import admin
from chemapp.models import UserProfile, Category, Page

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(UserProfile)
admin.site.register(Page)
# Register your models here.

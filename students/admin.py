from django.contrib import admin
from django import forms
from .models import StudentInfo

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "user", 
        "student_id",  
        "first_name",
        "second_name", 
        "middle_name",
        "last_name",
        "extension_name",
        "course", 
        "year_level", 
        "section"
    )

admin.site.register(StudentInfo)
from django.contrib import admin
from .models import Student, Assignment, Notice

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_no', 'full_name', 'department', 'semester')
    search_fields = ('roll_no', 'full_name')
    list_filter = ('department',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_code', 'due_date')
    list_filter = ('course_code',)
    search_fields = ('title',)

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'posted_at')
    list_filter = ('priority',)
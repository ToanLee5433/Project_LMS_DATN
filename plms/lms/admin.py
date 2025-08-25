from django.contrib import admin

from .models import Course, Lesson, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "title", "owner", "created_at")
    list_filter = ("created_at",)
    search_fields = ("code", "title", "description", "owner__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("code", "title", "description", "owner", "syllabus_url")
        }),
        ("Additional Data", {
            "fields": ("tags",)
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "title", "order", "duration")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    ordering = ("course", "order")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("course", "title", "content_url")
        }),
        ("Settings", {
            "fields": ("order", "duration", "tags")
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "user", "role_in_course", "status", "created_at")
    list_filter = ("role_in_course", "status", "created_at")
    search_fields = ("course__code", "course__title", "user__username", "user__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

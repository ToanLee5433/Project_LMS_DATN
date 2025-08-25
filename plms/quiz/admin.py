from django.contrib import admin
from .models import Quiz, Question, Attempt


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "strategy", "total_points", "created_at")
    list_filter = ("strategy", "course", "created_at")
    search_fields = ("title", "description", "course__title")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "total_points")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "description", "course", "owner")
        }),
        ("Quiz Settings", {
            "fields": ("strategy", "time_limit", "attempts_allowed", "total_points")
        }),
        ("Adaptive Settings", {
            "fields": ("max_questions", "min_questions", "tags"),
            "classes": ("collapse",),
            "description": "Configuration for adaptive quizzes"
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "order", "type", "difficulty", "points")
    list_filter = ("quiz", "type", "difficulty")
    search_fields = ("content", "quiz__title")
    ordering = ("quiz", "order")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("quiz", "type", "content", "order")
        }),
        ("Answer Configuration", {
            "fields": ("options", "answer_key", "points")
        }),
        ("Advanced Settings", {
            "fields": ("skill_tags", "difficulty"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "user", "score", "submitted", "start_at", "end_at")
    list_filter = ("submitted", "quiz", "start_at")
    search_fields = ("quiz__title", "user__username", "user__email")
    ordering = ("-start_at",)
    readonly_fields = ("start_at", "end_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("quiz", "user", "submitted")
        }),
        ("Results", {
            "fields": ("score", "ability_estimate", "detail")
        }),
        ("Timestamps", {
            "fields": ("start_at", "end_at"),
            "classes": ("collapse",)
        }),
    )

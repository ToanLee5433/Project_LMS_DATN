from django.contrib import admin
from .models import Quiz, Question, Attempt, AttemptReview


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


@admin.register(AttemptReview)
class AttemptReviewAdmin(admin.ModelAdmin):
    """Admin interface cho Spaced Repetition Reviews"""
    list_display = ("id", "user", "question_preview", "quality", "next_review", "interval", "repetition", "efactor")
    list_filter = ("quality", "next_review", "repetition", "last_review", "created_at")
    search_fields = ("user__username", "user__email", "question__content")
    ordering = ("next_review", "-last_review")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("user", "question", "attempt")
        }),
        ("Spaced Repetition Data", {
            "fields": ("quality", "interval", "repetition", "efactor")
        }),
        ("Schedule", {
            "fields": ("next_review", "last_review")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def question_preview(self, obj):
        """Hiển thị preview của question"""
        if obj.question and obj.question.content:
            return obj.question.content[:100] + "..." if len(obj.question.content) > 100 else obj.question.content
        return "-"
    question_preview.short_description = "Question Preview"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'question', 'attempt')
    
    # Thêm actions cho bulk operations
    actions = ['reset_reviews', 'mark_due_today']
    
    def reset_reviews(self, request, queryset):
        """Reset selected reviews về trạng thái ban đầu"""
        from datetime import date
        count = queryset.update(
            interval=1,
            repetition=0,
            efactor=2.5,
            next_review=date.today(),
            quality=3
        )
        self.message_user(request, f"Reset {count} reviews successfully.")
    reset_reviews.short_description = "Reset selected reviews"
    
    def mark_due_today(self, request, queryset):
        """Đánh dấu selected reviews cần ôn hôm nay"""
        from datetime import date
        count = queryset.update(next_review=date.today())
        self.message_user(request, f"Marked {count} reviews as due today.")
    mark_due_today.short_description = "Mark as due today"

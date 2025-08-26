from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from lms.models import Course


class Quiz(models.Model):
    STRATEGY = (("fixed", "fixed"), ("adaptive", "adaptive"))
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="quizzes"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_limit = models.PositiveIntegerField(null=True, blank=True)  # phút
    attempts_allowed = models.PositiveIntegerField(default=1)
    total_points = models.PositiveIntegerField(default=0)
    strategy = models.CharField(max_length=16, choices=STRATEGY, default="fixed")
    max_questions = models.PositiveIntegerField(null=True, blank=True, default=10)
    min_questions = models.PositiveIntegerField(null=True, blank=True, default=6)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_quizzes"
    )

    class Meta:
        app_label = 'quiz'
        indexes = [models.Index(fields=["course", "created_at"])]

    def __str__(self):
        return f"[{self.course.code}] {self.title}"

    def clean(self):
        if self.max_questions and self.min_questions and self.min_questions > self.max_questions:
            raise ValidationError("min_questions must be ≤ max_questions.")

    def save(self, *args, **kwargs):
        self.clean()  # ensure constraint
        super().save(*args, **kwargs)

    def recompute_total_points(self):
        total = self.questions.aggregate(total=models.Sum("points"))["total"] or 0
        if self.total_points != total:
            self.total_points = total
            super().save(update_fields=["total_points"])


class Question(models.Model):
    TYPE = (("mcq", "Multiple Choice"), ("fill", "Fill in the blank"))
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    type = models.CharField(max_length=8, choices=TYPE, default="mcq")
    content = models.TextField()
    options = models.JSONField(default=list, blank=True)
    answer_key = models.JSONField()
    skill_tags = models.JSONField(default=list, blank=True)
    difficulty = models.FloatField(default=0.5)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        app_label = 'quiz'
        ordering = ["order"]
        unique_together = ("quiz", "order")

    def __str__(self):
        return f"[{self.quiz.title}] Q{self.order}: {self.content[:50]}..."


class Attempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )
    start_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)
    ability_estimate = models.FloatField(default=0.5, null=True, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    submitted = models.BooleanField(default=False)

    class Meta:
        app_label = 'quiz'
        indexes = [models.Index(fields=["quiz", "user"])]

    def __str__(self):
        status = "Submitted" if self.submitted else "In Progress"
        return f"{self.user.username} - {self.quiz.title} ({status})"


class AttemptReview(models.Model):
    """
    Spaced Repetition model để theo dõi lịch ôn tập câu hỏi
    Sử dụng thuật toán SM-2 variant
    """
    attempt = models.ForeignKey(
        'Attempt', 
        on_delete=models.CASCADE, 
        related_name="reviews", 
        null=True, 
        blank=True
    )  # Liên kết với attempt gốc nếu cần
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quality = models.IntegerField(
        default=3, 
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )  # 0..5 (chất lượng nhớ)
    interval = models.PositiveIntegerField(default=1)  # ngày
    repetition = models.PositiveIntegerField(default=0)  # số lần lặp
    efactor = models.FloatField(default=2.5)  # ease factor
    next_review = models.DateField(default=date.today)  # ngày review tiếp theo
    last_review = models.DateField(null=True, blank=True)  # ngày review cuối cùng
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'quiz'
        unique_together = ("user", "question")
        indexes = [models.Index(fields=["user", "next_review"])]

    def clean(self):
        if self.quality < 0 or self.quality > 5:
            raise ValidationError("Quality must be between 0 and 5.")

    def __str__(self):
        return f"{self.user.username} - {self.question.content[:50]}... (Next: {self.next_review})"

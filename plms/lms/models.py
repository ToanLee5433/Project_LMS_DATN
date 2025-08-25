from django.conf import settings
from django.db import models


class Course(models.Model):
    code = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    syllabus_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_courses"
    )
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["code"]), models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{self.code} - {self.title}"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content_url = models.URLField()
    order = models.PositiveIntegerField(default=1)  # > 0
    duration = models.PositiveIntegerField(default=10)  # minutes
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["order"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"[{self.course.code}] {self.order}. {self.title}"


class Enrollment(models.Model):
    ROLE_IN_COURSE = (("teacher", "teacher"), ("student", "student"))
    STATUS = (("active", "active"), ("pending", "pending"), ("blocked", "blocked"))

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    role_in_course = models.CharField(
        max_length=8, choices=ROLE_IN_COURSE, default="student"
    )
    status = models.CharField(max_length=8, choices=STATUS, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "user")
        indexes = [models.Index(fields=["course", "user"])]

    def __str__(self):
        return f"{self.user.username} - {self.course.code} ({self.role_in_course})"

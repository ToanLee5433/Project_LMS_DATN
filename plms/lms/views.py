from django.conf import settings
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, serializers, viewsets
from rest_framework.throttling import ScopedRateThrottle

from .models import Course, Enrollment, Lesson
from .permissions import IsOwnerTeacherOrAdmin, IsTeacherOrAdmin
from .serializers import (CourseSerializer, EnrollmentSerializer,
                          LessonSerializer)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("owner").all().order_by("-created_at")
    serializer_class = CourseSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["title", "code"]
    filterset_fields = ["owner"]
    ordering_fields = ["created_at", "title", "code"]
    ordering = ["-created_at"]

    def get_permissions(self):
        # Đọc: công khai; Ghi: teacher/admin + owner/admin
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerTeacherOrAdmin()]


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related("course").all()
    serializer_class = LessonSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["title"]
    filterset_fields = ["course"]
    ordering_fields = ["order", "title", "duration"]
    ordering = ["order"]

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]

    def perform_create(self, serializer):
        """Chỉ owner của course (hoặc admin) mới được tạo lesson"""
        course = serializer.validated_data.get("course")
        user = self.request.user

        if user.role != "admin" and course.owner != user:
            raise serializers.ValidationError(
                {"course": "Chỉ chủ sở hữu khóa học hoặc admin mới được tạo bài học."}
            )
        serializer.save()

    def perform_update(self, serializer):
        """Chỉ owner của course (hoặc admin) mới được sửa lesson"""
        lesson = self.get_object()
        user = self.request.user

        if user.role != "admin" and lesson.course.owner != user:
            raise serializers.ValidationError(
                {
                    "detail": "Chỉ chủ khóa học hoặc admin mới được cập nhật bài học."
                }
            )
        serializer.save()

    def perform_destroy(self, instance):
        """Chỉ owner của course (hoặc admin) mới được xóa lesson"""
        user = self.request.user

        if user.role != "admin" and instance.course.owner != user:
            raise serializers.ValidationError(
                {"detail": "Chỉ chủ sở hữu khóa học hoặc admin mới được xóa bài học."}
            )
        instance.delete()


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related("course", "user").all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ["course", "user", "role_in_course", "status"]
    search_fields = ["course__code", "user__username"]

    def get_throttles(self):
        """Only apply throttle in production"""
        if settings.DEBUG:
            return []
        self.throttle_scope = "enrollments"
        return [ScopedRateThrottle()]

    def perform_create(self, serializer):
        data = serializer.validated_data
        user = self.request.user
        # student chỉ tự-enroll
        if data.get("role_in_course") == "student" and data.get("user") != user:
            raise serializers.ValidationError(
                {"user": "Sinh viên chỉ có thể tự ghi danh."}
            )
        # enroll teacher chỉ teacher/admin
        if data.get("role_in_course") == "teacher" and user.role not in (
            "teacher",
            "admin",
        ):
            raise serializers.ValidationError(
                {"role_in_course": "Chỉ teacher/admin được ghi danh làm giáo viên."}
            )

        try:
            serializer.save()
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "Bạn đã ghi danh khóa học này rồi."}
            )

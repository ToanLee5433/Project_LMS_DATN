from django.db import IntegrityError
from rest_framework import serializers

from .models import Course, Enrollment, Lesson


class CourseSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "code",
            "title",
            "description",
            "syllabus_url",
            "owner",
            "owner_name",
            "tags",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "owner"]

    def validate_code(self, value):
        """Chuẩn hóa code: uppercase và strip"""
        return value.strip().upper()

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class LessonSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.code", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "course_code",
            "title",
            "content_url",
            "order",
            "duration",
            "tags",
        ]

    # VALIDATION: order > 0 và không trùng trong cùng course
    def validate(self, data):
        course = data.get("course") or getattr(self.instance, "course", None)
        order = data.get("order")

        # Check order > 0 - must explicitly check for 0 value
        if "order" in data and data["order"] <= 0:
            raise serializers.ValidationError(
                {"order": "Thứ tự bài học phải lớn hơn 0."}
            )

        # Check unique order within course
        if order and course:
            from .models import Lesson

            qs = Lesson.objects.filter(course=course, order=order)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"order": "Thứ tự này đã tồn tại cho khóa học."}
                )
        return data


class EnrollmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.code", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "course_code",
            "user",
            "username",
            "role_in_course",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        """Check for duplicate enrollment"""
        course = data.get("course")
        user = data.get("user")

        if course and user:
            from .models import Enrollment

            qs = Enrollment.objects.filter(course=course, user=user)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"detail": "Bạn đã ghi danh khóa học này rồi."}
                )
        return data

    def create(self, validated_data):
        """Override create to catch IntegrityError and provide custom message"""
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "Bạn đã ghi danh khóa học này rồi."}
            )

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from lms.models import Course, Enrollment, Lesson


class Command(BaseCommand):
    help = "Seed demo courses/lessons/enrollments"

    def handle(self, *args, **opts):
        U = get_user_model()

        teacher, _ = U.objects.get_or_create(
            username="teacher1", defaults={"email": "t1@example.com", "role": "teacher"}
        )
        teacher.set_password(os.getenv("SEED_PASSWORD", "SecurePass123!"))
        teacher.save()

        c, _ = Course.objects.get_or_create(
            code="DSA101",
            defaults={
                "title": "Cấu trúc dữ liệu",
                "owner": teacher,
                "tags": ["array", "tree"],
            },
        )
        c2, _ = Course.objects.get_or_create(
            code="WEB101",
            defaults={
                "title": "Phát triển Web",
                "owner": teacher,
                "tags": ["html", "css"],
            },
        )

        for i in range(1, 6):
            Lesson.objects.get_or_create(
                course=c,
                order=i,
                defaults={
                    "title": f"Bài {i}: Chủ đề {i}",
                    "content_url": "https://example.com/slide.pdf",
                    "duration": 12,
                    "tags": ["array"] if i <= 3 else ["tree"],
                },
            )

        U.objects.filter(username="sv01").delete()
        student = U.objects.create_user(
            username="sv01",
            email="sv01@example.com",
            password="Abcd1234!",
            role="student",
        )
        Enrollment.objects.get_or_create(
            course=c, user=student, defaults={"role_in_course": "student"}
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded LMS demo (teacher1, DSA101, WEB101, 5 lessons, sv01 enrolled)"
            )
        )

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .models import Course, Enrollment, Lesson

User = get_user_model()


@override_settings(DEBUG=True)  # Ensure DEBUG is True for tests
class LMSTestCase(TestCase):
    def setUp(self):
        """Setup test data"""
        # Tạo users
        self.admin = User.objects.create_user(
            username="admin", email="admin@test.com", password="adminpass", role="admin"
        )
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@test.com",
            password="teacherpass",
            role="teacher",
        )
        self.teacher2 = User.objects.create_user(
            username="teacher2",
            email="teacher2@test.com",
            password="teacherpass",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="studentpass",
            role="student",
        )

        # Tạo course
        self.course = Course.objects.create(
            code="TEST101",
            title="Test Course",
            description="Test description",
            syllabus_url="http://example.com/syllabus",
            owner=self.teacher,
        )

        # API client
        self.client = APIClient()

    def test_student_cannot_create_course(self):
        """Test case 1: student không tạo được course (403)"""
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            "/api/lms/courses/",
            {
                "code": "STU101",
                "title": "Student Course",
                "description": "Test by student",
                "syllabus_url": "http://example.com",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_only_create_lesson_for_owned_course(self):
        """Test case 2: teacher tạo lesson chỉ khi là owner course"""
        # teacher2 (không phải owner) cố tạo lesson cho course của teacher
        self.client.force_authenticate(user=self.teacher2)

        response = self.client.post(
            "/api/lms/lessons/",
            {
                "course": self.course.id,
                "title": "Unauthorized Lesson",
                "content_url": "http://example.com/content",
                "order": 1,
                "duration": 30,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("chủ sở hữu khóa học", str(response.data).lower())

    def test_teacher_can_create_lesson_for_own_course(self):
        """Test case: teacher có thể tạo lesson cho course của mình"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            "/api/lms/lessons/",
            {
                "course": self.course.id,
                "title": "Authorized Lesson",
                "content_url": "http://example.com/content",
                "order": 1,
                "duration": 30,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_lesson_for_any_course(self):
        """Test case: admin có thể tạo lesson cho bất kỳ course nào"""
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/lms/lessons/",
            {
                "course": self.course.id,
                "title": "Admin Lesson",
                "content_url": "http://example.com/content",
                "order": 2,
                "duration": 45,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_enrollment_returns_400(self):
        """Test case 3: enroll trùng → 400 với message thân thiện"""
        self.client.force_authenticate(user=self.student)

        # Enrollment lần 1 - thành công
        response1 = self.client.post(
            "/api/lms/enrollments/",
            {
                "course": self.course.id,
                "user": self.student.id,
                "role_in_course": "student",
            },
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Enrollment lần 2 - thất bại
        response2 = self.client.post(
            "/api/lms/enrollments/",
            {
                "course": self.course.id,
                "user": self.student.id,
                "role_in_course": "student",
            },
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        # Accept either custom message or Django's default unique constraint message
        response_str = str(response2.data).lower()
        self.assertTrue(
            "đã ghi danh" in response_str or "unique" in response_str,
            f"Expected duplicate enrollment error message, got: {response2.data}",
        )

    def test_course_code_normalization(self):
        """Test case: code được chuẩn hóa uppercase"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            "/api/lms/courses/",
            {
                "code": "  web102  ",  # có space và lowercase
                "title": "Web Development",
                "description": "Test normalization",
                "syllabus_url": "http://example.com",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["code"], "WEB102")

    def test_lesson_order_validation(self):
        """Test case: Lesson order phải > 0"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            "/api/lms/lessons/",
            {
                "course": self.course.id,
                "title": "Invalid Order Lesson",
                "content_url": "http://example.com/content",
                "order": 0,  # Invalid: phải > 0
                "duration": 30,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order", response.data)

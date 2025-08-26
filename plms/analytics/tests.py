"""
Tests for Analytics App
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from lms.models import Course, Enrollment
from quiz.models import Quiz, Question

User = get_user_model()


class TeacherAnalyticsTests(TestCase):
    """Test teacher analytics endpoints"""
    
    def setUp(self):
        """Tạo test data"""
        self.teacher = User.objects.create_user(
            username='teacher', 
            password='pass',
            email='teacher@test.com',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='student',
            password='pass',
            email='student@test.com',
            role='student'
        )
        
        self.course = Course.objects.create(
            code='TEST001',
            title='Test Course',
            description='Test Course Description',
            owner=self.teacher
        )
        
        # Enroll teacher and student
        Enrollment.objects.create(
            course=self.course,
            user=self.teacher,
            role_in_course='teacher'
        )
        Enrollment.objects.create(
            course=self.course,
            user=self.student,
            role_in_course='student'
        )
        
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            course=self.course,
            max_questions=5,
            min_questions=3,
            time_limit=30,
            owner=self.teacher
        )
        
        self.question = Question.objects.create(
            content='Test question?',
            quiz=self.quiz,
            type='mcq',
            answer_key=['A'],
            difficulty=0.5
        )
        
        self.client = APIClient()

    def test_teacher_analytics_success(self):
        """Test teacher có thể xem analytics của course mình"""
        self.client.force_authenticate(user=self.teacher)
        
        url = reverse('teacher_analytics', kwargs={'course_id': self.course.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('course_info', response.data)
        self.assertIn('avg_score', response.data)
        self.assertIn('total_attempts', response.data)
        self.assertIn('score_distribution', response.data)
        self.assertEqual(response.data['course_info']['id'], self.course.id)

    def test_teacher_analytics_unauthenticated(self):
        """Test unauthorized user không thể truy cập"""
        url = reverse('teacher_analytics', kwargs={'course_id': self.course.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StudentAnalyticsTests(TestCase):
    """Test student dashboard endpoints"""
    
    def setUp(self):
        self.student = User.objects.create_user(
            username='student',
            password='pass',
            email='student@test.com', 
            role='student'
        )
        
        self.client = APIClient()

    def test_student_dashboard_success(self):
        """Test student có thể xem dashboard của mình"""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('student_dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_courses', response.data)
        self.assertIn('total_quizzes_taken', response.data)


class AdminAnalyticsTests(TestCase):
    """Test admin stats endpoints"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='pass',
            email='admin@test.com',
            role='admin'
        )
        
        self.client = APIClient()

    def test_admin_stats_success(self):
        """Test admin có thể xem system stats"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('admin_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('total_courses', response.data)

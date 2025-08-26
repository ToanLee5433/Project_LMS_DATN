from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from quiz.models import AttemptReview, Question, Quiz
from quiz.sr_utils import sm2, calculate_next_review
from lms.models import Course

User = get_user_model()


class SpacedRepetitionTests(TestCase):
    """Test các chức năng Spaced Repetition"""

    def setUp(self):
        """Tạo test data cho spaced repetition"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@test.com'
        )
        
        self.teacher = User.objects.create_user(
            username='teacher',
            password='teachpass',
            email='teacher@test.com',
            role='teacher'
        )
        
        self.course = Course.objects.create(
            code='TEST001',
            title='Test Course',
            description='Test',
            owner=self.teacher
        )
        
        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Test Quiz',
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
        self.client.force_authenticate(user=self.user)

    def test_sm2_algorithm(self):
        """Test SM-2 algorithm hoạt động đúng"""
        # Quality = 5 (perfect recall)
        interval, repetition, efactor = sm2(5, 1, 0, 2.5)
        self.assertEqual(interval, 1)
        self.assertEqual(repetition, 1)
        self.assertEqual(efactor, 2.6)
        
        # Quality = 0 (complete blackout)
        interval, repetition, efactor = sm2(0, 6, 3, 2.5)
        self.assertEqual(interval, 1)
        self.assertEqual(repetition, 0)
        self.assertLess(efactor, 2.5)

    def test_sr_review_api_get_due(self):
        """Test API lấy questions cần review"""
        # Tạo AttemptReview đã due
        AttemptReview.objects.create(
            user=self.user,
            question=self.question,
            quality=3,
            interval=1,
            repetition=1,
            efactor=2.5,
            next_review=date.today() - timedelta(days=1)  # Due yesterday
        )
        
        url = reverse('sr_reviews')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['reviews']), 1)
        self.assertEqual(response.data['reviews'][0]['question_id'], self.question.id)

    def test_sr_review_api_post_quality(self):
        """Test API cập nhật quality score"""
        review = AttemptReview.objects.create(
            user=self.user,
            question=self.question,
            quality=3,
            interval=1,
            repetition=1,
            efactor=2.5,
            next_review=date.today() - timedelta(days=1)
        )
        
        url = reverse('sr_reviews')
        data = {
            'question_id': self.question.id,
            'quality': 5
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify update
        review.refresh_from_db()
        self.assertEqual(review.quality, 5)
        self.assertGreater(review.next_review, date.today())

    def test_sr_stats_api(self):
        """Test API thống kê SR"""
        AttemptReview.objects.create(
            user=self.user,
            question=self.question,
            quality=3,
            interval=6,
            repetition=2,
            efactor=2.5,
            next_review=date.today() + timedelta(days=3)
        )
        
        url = reverse('sr_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_reviews'], 1)
        self.assertEqual(response.data['reviews_due_today'], 0)
        self.assertEqual(response.data['overdue_reviews'], 0)

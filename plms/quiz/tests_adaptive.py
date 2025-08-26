from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from lms.models import Course, Enrollment
from quiz.models import Quiz, Question, Attempt
from quiz.adaptive import update_theta, pick_next_question


User = get_user_model()


class AdaptiveQuizTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create users
        self.teacher = User.objects.create_user(
            username="teacher_test",
            email="teacher@test.com",
            password="password123",
            role="teacher"
        )
        
        self.student = User.objects.create_user(
            username="student_test", 
            email="student@test.com",
            password="password123",
            role="student"
        )
        
        # Create course and enrollment
        self.course = Course.objects.create(
            title="Test Course",
            code="TEST101",
            owner=self.teacher
        )
        
        self.enrollment = Enrollment.objects.create(
            course=self.course,
            user=self.student,
            status="active",
            role_in_course="student"
        )
        
        # Create adaptive quiz
        self.quiz = Quiz.objects.create(
            course=self.course,
            title="Test Adaptive Quiz",
            strategy="adaptive",
            owner=self.teacher,
            max_questions=5,
            min_questions=3,
            time_limit=30
        )
        
        # Create questions with different difficulties
        questions_data = [
            ("What is 2+2?", "mcq", ["3", "4", "5"], 1, 0.2, 1),
            ("Capital of France?", "fill", [], "Paris", 0.5, 2),  
            ("Solve x^2 + 5x + 6 = 0", "mcq", ["x=-2,-3", "x=2,3", "x=1,6"], 0, 0.8, 3),
        ]
        
        for i, (content, q_type, options, answer_key, difficulty, points) in enumerate(questions_data):
            Question.objects.create(
                quiz=self.quiz,
                order=i+1,
                content=content,
                type=q_type,
                options=options,
                answer_key=answer_key,
                difficulty=difficulty,
                points=points
            )
        
        self.client = APIClient()

    def test_adaptive_start_success(self):
        """Test successful adaptive quiz start"""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('adaptive_start', kwargs={'quiz_id': self.quiz.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attempt_id', response.data)
        self.assertIn('question', response.data)
        
        # Check attempt was created
        attempt = Attempt.objects.get(id=response.data['attempt_id'])
        self.assertEqual(attempt.ability_estimate, 0.5)
        self.assertEqual(len(attempt.detail['asked_ids']), 1)

    def test_adaptive_start_non_adaptive_quiz(self):
        """Test start with non-adaptive quiz fails"""
        fixed_quiz = Quiz.objects.create(
            course=self.course,
            title="Fixed Quiz",
            strategy="fixed",
            owner=self.teacher
        )
        
        self.client.force_authenticate(user=self.student)
        url = reverse('adaptive_start', kwargs={'quiz_id': fixed_quiz.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('không phải adaptive', response.data['detail'])

    def test_adaptive_answer_success(self):
        """Test successful answer submission"""
        self.client.force_authenticate(user=self.student)
        
        # Start quiz
        start_url = reverse('adaptive_start', kwargs={'quiz_id': self.quiz.id})
        start_response = self.client.post(start_url)
        attempt_id = start_response.data['attempt_id']
        question_id = start_response.data['question']['question_id']
        
        # Submit answer
        answer_url = reverse('adaptive_answer', kwargs={'attempt_id': attempt_id})
        answer_data = {
            'question_id': question_id,
            'given': 1  # Correct answer for first question
        }
        response = self.client.post(answer_url, answer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ability', response.data)
        
        # Check ability was updated
        attempt = Attempt.objects.get(id=attempt_id)
        self.assertNotEqual(attempt.ability_estimate, 0.5)

    def test_adaptive_answer_invalid_question(self):
        """Test answer submission with invalid question_id"""
        self.client.force_authenticate(user=self.student)
        
        # Start quiz
        start_url = reverse('adaptive_start', kwargs={'quiz_id': self.quiz.id})
        start_response = self.client.post(start_url)
        attempt_id = start_response.data['attempt_id']
        
        # Submit answer with invalid question_id
        answer_url = reverse('adaptive_answer', kwargs={'attempt_id': attempt_id})
        answer_data = {
            'question_id': 9999,  # Invalid ID
            'given': 1
        }
        response = self.client.post(answer_url, answer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_adaptive_finish_success(self):
        """Test successful quiz finish"""
        self.client.force_authenticate(user=self.student)
        
        # Start quiz
        start_url = reverse('adaptive_start', kwargs={'quiz_id': self.quiz.id})
        start_response = self.client.post(start_url)
        attempt_id = start_response.data['attempt_id']
        
        # Answer minimum required questions
        for i in range(3):  # min_questions = 3
            question_id = start_response.data['question']['question_id']
            answer_url = reverse('adaptive_answer', kwargs={'attempt_id': attempt_id})
            answer_data = {'question_id': question_id, 'given': 1}
            answer_response = self.client.post(answer_url, answer_data, format='json')
            
            if not answer_response.data.get('done', False):
                start_response.data['question'] = answer_response.data.get('next_question')
        
        # Finish quiz
        finish_url = reverse('adaptive_finish', kwargs={'attempt_id': attempt_id})
        response = self.client.post(finish_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('score', response.data)
        self.assertIn('ability', response.data)
        
        # Check attempt is marked as submitted
        attempt = Attempt.objects.get(id=attempt_id)
        self.assertTrue(attempt.submitted)

    def test_adaptive_status(self):
        """Test status endpoint"""
        self.client.force_authenticate(user=self.student)
        
        # Start quiz
        start_url = reverse('adaptive_start', kwargs={'quiz_id': self.quiz.id})
        start_response = self.client.post(start_url)
        attempt_id = start_response.data['attempt_id']
        
        # Get status
        status_url = reverse('adaptive_status', kwargs={'attempt_id': attempt_id})
        response = self.client.get(status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attempt_id', response.data)
        self.assertIn('ability', response.data)
        self.assertIn('asked_ids', response.data)

    def test_update_theta_algorithm(self):
        """Test theta update algorithm"""
        initial_theta = 0.5
        difficulty = 0.3
        
        # Test correct answer (should increase theta)
        new_theta = update_theta(initial_theta, difficulty, True)
        self.assertGreater(new_theta, initial_theta)
        
        # Test wrong answer (should decrease theta)  
        new_theta = update_theta(initial_theta, difficulty, False)
        self.assertLess(new_theta, initial_theta)
        
        # Test boundary conditions
        self.assertLessEqual(new_theta, 1.0)
        self.assertGreaterEqual(new_theta, 0.0)

    def test_pick_next_question_algorithm(self):
        """Test question selection algorithm"""
        questions = list(self.quiz.questions.all())
        asked_qids = {questions[0].id}  # First question already asked
        theta = 0.5
        
        next_q = pick_next_question(questions, asked_qids, theta)
        
        # Should not pick already asked question
        self.assertNotEqual(next_q.id, questions[0].id)
        
        # Should pick question closest to theta
        distances = [abs(q.difficulty - theta) for q in questions[1:]]
        min_distance = min(distances)
        expected_difficulty = None
        for q in questions[1:]:
            if abs(q.difficulty - theta) == min_distance:
                expected_difficulty = q.difficulty
                break
        
        self.assertEqual(next_q.difficulty, expected_difficulty)

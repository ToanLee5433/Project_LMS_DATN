"""
Seed Analytics and Spaced Repetition Data
Management command để tạo dữ liệu mẫu cho analytics và SR
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta
import random

from lms.models import Course
from quiz.models import Quiz, Attempt, Question, AttemptReview
from quiz.sr_utils import update_review_after_attempt

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed analytics and SR data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--attempts',
            type=int,
            default=20,
            help='Number of sample attempts to create'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=50,
            help='Number of SR reviews to create'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting analytics data seeding...'))
        
        # Lấy hoặc tạo users
        teacher = self.get_or_create_teacher()
        students = self.get_or_create_students(count=5)
        
        # Lấy hoặc tạo course và quiz
        course = self.get_or_create_course(teacher)
        quiz = self.get_or_create_quiz(course, teacher)
        questions = self.get_or_create_questions(quiz)
        
        # Tạo attempts mẫu
        attempts_count = options['attempts']
        self.create_sample_attempts(quiz, students, questions, attempts_count)
        
        # Tạo SR reviews mẫu
        reviews_count = options['reviews']
        self.create_sample_reviews(students, questions, reviews_count)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded {attempts_count} attempts and {reviews_count} reviews'
            )
        )
    
    def get_or_create_teacher(self):
        """Lấy hoặc tạo teacher"""
        teacher, created = User.objects.get_or_create(
            username='analytics_teacher',
            defaults={
                'email': 'teacher@analytics.test',
                'first_name': 'Analytics',
                'last_name': 'Teacher',
                'role': 'teacher'
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
            self.stdout.write('Created teacher user')
        return teacher
    
    def get_or_create_students(self, count=5):
        """Lấy hoặc tạo students"""
        students = []
        for i in range(1, count + 1):
            student, created = User.objects.get_or_create(
                username=f'analytics_student_{i}',
                defaults={
                    'email': f'student{i}@analytics.test',
                    'first_name': f'Student',
                    'last_name': f'{i}',
                    'role': 'student'
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                self.stdout.write(f'Created student {i}')
            students.append(student)
        return students
    
    def get_or_create_course(self, teacher):
        """Lấy hoặc tạo course"""
        course, created = Course.objects.get_or_create(
            code='ANALYTICS101',
            defaults={
                'title': 'Analytics Test Course',
                'description': 'Course for testing analytics functionality',
                'owner': teacher
            }
        )
        if created:
            self.stdout.write('Created analytics course')
        return course
    
    def get_or_create_quiz(self, course, teacher):
        """Lấy hoặc tạo quiz"""
        quiz, created = Quiz.objects.get_or_create(
            title='Analytics Quiz',
            course=course,
            defaults={
                'description': 'Quiz for testing analytics',
                'strategy': 'fixed',
                'time_limit': 30,
                'attempts_allowed': 3,
                'owner': teacher
            }
        )
        if created:
            self.stdout.write('Created analytics quiz')
        return quiz
    
    def get_or_create_questions(self, quiz):
        """Lấy hoặc tạo questions"""
        if quiz.questions.exists():
            return list(quiz.questions.all())
        
        skills = ['math', 'logic', 'programming', 'science', 'language']
        questions = []
        
        for i in range(1, 11):  # 10 questions
            question = Question.objects.create(
                quiz=quiz,
                type='mcq',
                content=f'Analytics test question {i}?',
                options=[f'Option A{i}', f'Option B{i}', f'Option C{i}', f'Option D{i}'],
                answer_key=[f'Option A{i}'],  # First option is always correct
                skill_tags=[random.choice(skills)],
                difficulty=round(random.uniform(0.2, 0.8), 2),
                points=random.randint(1, 5),
                order=i
            )
            questions.append(question)
        
        # Recompute total points
        quiz.recompute_total_points()
        
        self.stdout.write(f'Created {len(questions)} questions')
        return questions
    
    def create_sample_attempts(self, quiz, students, questions, count):
        """Tạo sample attempts"""
        created = 0
        
        for _ in range(count):
            student = random.choice(students)
            
            # Tạo attempt
            attempt = Attempt.objects.create(
                quiz=quiz,
                user=student,
                submitted=True,
                start_at=self.random_datetime_past(days=30),
                end_at=None
            )
            
            # Set end_at
            attempt.end_at = attempt.start_at + timedelta(minutes=random.randint(10, 30))
            
            # Tạo answers
            answers = []
            correct_count = 0
            
            # Random subset of questions
            selected_questions = random.sample(questions, random.randint(5, len(questions)))
            
            for question in selected_questions:
                # 70% chance of correct answer
                correct = random.random() < 0.7
                if correct:
                    correct_count += 1
                
                answers.append({
                    'question_id': question.id,
                    'user_answer': question.answer_key[0] if correct else random.choice(question.options),
                    'correct_answer': question.answer_key[0],
                    'correct': correct,
                    'points': question.points if correct else 0,
                    'difficulty': question.difficulty
                })
            
            # Calculate score
            total_points = sum(q.points for q in selected_questions)
            earned_points = sum(a['points'] for a in answers)
            score = (earned_points / total_points * 10) if total_points > 0 else 0
            
            # Update attempt
            attempt.score = round(score, 2)
            attempt.detail = {
                'answers': answers,
                'total_questions': len(answers),
                'correct_answers': correct_count
            }
            attempt.save()
            
            created += 1
        
        self.stdout.write(f'Created {created} sample attempts')
    
    def create_sample_reviews(self, students, questions, count):
        """Tạo sample SR reviews"""
        created = 0
        
        for _ in range(count):
            student = random.choice(students)
            question = random.choice(questions)
            
            # Kiểm tra xem review đã tồn tại chưa
            if AttemptReview.objects.filter(user=student, question=question).exists():
                continue
            
            # Tạo random review data
            correct = random.random() < 0.6  # 60% correct rate
            
            # Sử dụng SR utils để tạo review
            review = update_review_after_attempt(
                user=student,
                question=question,
                correct=correct
            )
            
            # Randomize some fields để tạo variety
            review.repetition = random.randint(0, 5)
            review.interval = random.choice([1, 2, 6, 12, 25, 50])
            review.efactor = round(random.uniform(1.3, 3.5), 2)
            
            # Random next_review date
            days_offset = random.randint(-7, 30)  # Some overdue, some future
            review.next_review = date.today() + timedelta(days=days_offset)
            
            # Random last_review
            if review.repetition > 0:
                review.last_review = date.today() - timedelta(
                    days=random.randint(1, review.interval * 2)
                )
            
            review.save()
            created += 1
        
        self.stdout.write(f'Created {created} sample SR reviews')
    
    def random_datetime_past(self, days=30):
        """Generate random datetime in the past"""
        from django.utils import timezone
        now = timezone.now()
        random_days = random.randint(1, days)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        
        return now - timedelta(
            days=random_days,
            hours=random_hours,
            minutes=random_minutes
        )

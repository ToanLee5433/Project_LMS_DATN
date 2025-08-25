from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User
from lms.models import Course, Enrollment
from quiz.models import Quiz, Question, Attempt


class Command(BaseCommand):
    help = 'Create sample quiz data for testing'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("🎯 Creating sample quiz data...")
            
            # Get or create users and courses
            teacher = User.objects.filter(role='teacher').first()
            student = User.objects.filter(role='student').first()
            course = Course.objects.first()
            
            if not teacher:
                teacher = User.objects.create_user(
                    username='quiz_teacher',
                    email='teacher@quiz.com',
                    password='password123',
                    role='teacher',
                    first_name='Quiz',
                    last_name='Teacher'
                )
                self.stdout.write(f"✅ Created teacher: {teacher.username}")
            
            if not student:
                student = User.objects.create_user(
                    username='quiz_student',
                    email='student@quiz.com',
                    password='password123',
                    role='student',
                    first_name='Quiz',
                    last_name='Student'
                )
                self.stdout.write(f"✅ Created student: {student.username}")
            
            if not course:
                course = Course.objects.create(
                    code="QUIZ101",
                    title="Quiz Test Course",
                    description="Course for testing quiz functionality",
                    owner=teacher,
                    status="published"
                )
                self.stdout.write(f"✅ Created course: {course.code}")
            
            # Ensure student is enrolled
            enrollment, created = Enrollment.objects.get_or_create(
                user=student,
                course=course,
                defaults={'status': 'active'}
            )
            if created:
                self.stdout.write(f"✅ Enrolled {student.username} in {course.code}")
            
            # Create quizzes
            quiz1 = Quiz.objects.create(
                course=course,
                title="Python Basics Quiz",
                description="Test your knowledge of Python fundamentals",
                time_limit=30,  # 30 minutes
                attempts_allowed=2,
                strategy="fixed",
                tags=["python", "programming", "basics"],
                owner=teacher
            )
            self.stdout.write(f"✅ Created quiz: {quiz1.title}")
            
            quiz2 = Quiz.objects.create(
                course=course,
                title="Web Development Quiz",
                description="HTML, CSS, and JavaScript basics",
                time_limit=45,
                attempts_allowed=1,
                strategy="fixed",
                tags=["html", "css", "javascript", "web"],
                owner=teacher
            )
            self.stdout.write(f"✅ Created quiz: {quiz2.title}")
            
            # Create questions for Quiz 1 (Python Basics)
            questions_quiz1 = [
                {
                    "type": "mcq",
                    "content": "What is the output of print('Hello' + ' ' + 'World')?",
                    "options": ["Hello World", "HelloWorld", "Error", "None"],
                    "answer_key": 0,
                    "skill_tags": ["python", "strings"],
                    "difficulty": 0.3,
                    "points": 2
                },
                {
                    "type": "mcq", 
                    "content": "Which of the following are mutable data types in Python?",
                    "options": ["List", "Tuple", "String", "Integer"],
                    "answer_key": [0],  # Multiple correct answers
                    "skill_tags": ["python", "data-types"],
                    "difficulty": 0.5,
                    "points": 3
                },
                {
                    "type": "fill",
                    "content": "Complete the code: def my_function(): _____ 'Hello World'",
                    "options": [],
                    "answer_key": ["return", "Return"],
                    "skill_tags": ["python", "functions"],
                    "difficulty": 0.4,
                    "points": 2
                },
                {
                    "type": "mcq",
                    "content": "What does the len() function return?",
                    "options": ["The length of an object", "The last element", "The first element", "None of the above"],
                    "answer_key": 0,
                    "skill_tags": ["python", "built-in-functions"],
                    "difficulty": 0.2,
                    "points": 1
                }
            ]
            
            for i, q_data in enumerate(questions_quiz1, 1):
                Question.objects.create(
                    quiz=quiz1,
                    order=i,
                    **q_data
                )
            
            # Create questions for Quiz 2 (Web Development)
            questions_quiz2 = [
                {
                    "type": "mcq",
                    "content": "Which HTML tag is used for the largest heading?",
                    "options": ["<h1>", "<h6>", "<header>", "<big>"],
                    "answer_key": 0,
                    "skill_tags": ["html", "headings"],
                    "difficulty": 0.2,
                    "points": 1
                },
                {
                    "type": "fill",
                    "content": "In CSS, which property is used to change the text color? _____: red;",
                    "options": [],
                    "answer_key": ["color"],
                    "skill_tags": ["css", "properties"],
                    "difficulty": 0.3,
                    "points": 2
                },
                {
                    "type": "mcq",
                    "content": "Which JavaScript method is used to add an element to the end of an array?",
                    "options": ["push()", "pop()", "shift()", "unshift()"],
                    "answer_key": 0,
                    "skill_tags": ["javascript", "arrays"],
                    "difficulty": 0.4,
                    "points": 2
                }
            ]
            
            for i, q_data in enumerate(questions_quiz2, 1):
                Question.objects.create(
                    quiz=quiz2,
                    order=i,
                    **q_data
                )
            
            # Recompute total points
            quiz1.recompute_total_points()
            quiz2.recompute_total_points()
            
            self.stdout.write(f"✅ Created {len(questions_quiz1)} questions for {quiz1.title}")
            self.stdout.write(f"✅ Created {len(questions_quiz2)} questions for {quiz2.title}")
            
            # Create a sample attempt
            attempt = Attempt.objects.create(
                quiz=quiz1,
                user=student
            )
            self.stdout.write(f"✅ Created sample attempt for {student.username}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎯 Sample quiz data created successfully!\n"
                    f"📚 Courses: {Course.objects.count()}\n"
                    f"🎯 Quizzes: {Quiz.objects.count()}\n" 
                    f"❓ Questions: {Question.objects.count()}\n"
                    f"📝 Attempts: {Attempt.objects.count()}\n"
                    f"👥 Users: {User.objects.count()}\n"
                )
            )

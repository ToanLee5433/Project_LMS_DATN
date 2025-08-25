from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.models import Course, Enrollment
from quiz.models import Quiz, Question


class Command(BaseCommand):
    help = "Seed adaptive quiz with questions of varying difficulty"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        # Get teacher and course
        teacher = User.objects.get(username="teacher1")
        course = Course.objects.get(code="DSA101")
        
        # Create or get adaptive quiz
        quiz, created = Quiz.objects.get_or_create(
            course=course,
            title="Adaptive DSA Quiz",
            defaults={
                "strategy": "adaptive",
                "owner": teacher,
                "max_questions": 10,
                "min_questions": 6,
                "description": "Adaptive quiz that adjusts to your ability level",
                "time_limit": 30  # 30 minutes
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created adaptive quiz: {quiz.title}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Quiz already exists: {quiz.title}")
            )
        
        # Question data with varying difficulty (0.2 to 0.95)
        question_data = [
            (1, "fill", "Ký hiệu viết tắt của 'First In First Out'?", None, "FIFO", 0.2, 1),
            (2, "mcq", "Cấu trúc dữ liệu LIFO là?", ["Queue", "Stack", "Deque"], 1, 0.3, 2),
            (3, "mcq", "Tìm kiếm nhị phân cần mảng ...?", ["bất kỳ", "đã sắp xếp"], 1, 0.4, 2),
            (4, "mcq", "Độ phức tạp trung bình của quicksort?", ["O(n)", "O(n log n)", "O(n^2)"], 1, 0.5, 3),
            (5, "mcq", "Cây cân bằng chiều cao là?", ["AVL", "Trie", "Heap"], 0, 0.6, 3),
            (6, "mcq", "Số đỉnh của cây nhị phân hoàn chỉnh độ cao h là?", ["2^h", "2^(h+1)-1", "h^2"], 1, 0.7, 4),
            (7, "fill", "Cấu trúc dữ liệu ưu tiên phần tử lớn nhất gọi là __.", None, "heap", 0.8, 4),
            (8, "mcq", "Độ phức tạp tệ nhất của heapsort?", ["O(n log n)", "O(n^2)", "O(log n)"], 0, 0.85, 4),
            (9, "fill", "Tên cấu trúc cây với mỗi node với ≤2 con là __.", None, "binary tree", 0.9, 4),
            (10, "mcq", "Red-Black tree đảm bảo độ cao tối đa là?", ["2 log(n+1)", "3 log(n+1)", "log(n)"], 0, 0.95, 5),
        ]
        
        created_count = 0
        for order, q_type, content, options, answer_key, difficulty, points in question_data:
            question, created = Question.objects.get_or_create(
                quiz=quiz,
                order=order,
                defaults={
                    "type": q_type,
                    "content": content,
                    "options": options or [],
                    "answer_key": answer_key,
                    "difficulty": difficulty,
                    "points": points,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Created Q{order}: {content[:50]}...")
        
        self.stdout.write(
            self.style.SUCCESS(f"Created {created_count} new questions")
        )
        
        # Ensure student is enrolled
        student = User.objects.get(username="sv01")
        enrollment, created = Enrollment.objects.get_or_create(
            course=course,
            user=student,
            defaults={
                "role_in_course": "student",
                "status": "active"
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Enrolled {student.username} in {course.code}")
            )
        
        # Recompute quiz total points
        quiz.recompute_total_points()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Adaptive quiz setup complete! "
                f"Quiz ID: {quiz.id}, Total Points: {quiz.total_points}"
            )
        )

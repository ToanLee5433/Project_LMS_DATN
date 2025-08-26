"""
Analytics Views - Teacher/Student/Admin Dashboard APIs
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Avg, Count, Q, F, Case, When, IntegerField
from django.db.models.functions import TruncMonth
from datetime import date
from django.contrib.auth import get_user_model

from lms.models import Course
from quiz.models import Attempt, Question, Quiz, AttemptReview
from .serializers import (
    TeacherAnalyticsSerializer,
    StudentDashboardSerializer, 
    AdminStatsSerializer
)

User = get_user_model()


class TeacherCourseAnalyticsAPI(APIView):
    """
    Analytics cho Teacher - thống kê course performance
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        # Kiểm tra quyền teacher
        if request.user.role != 'teacher':
            return Response(
                {"detail": "Permission denied. Teacher role required."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Kiểm tra course ownership
            course = Course.objects.get(pk=course_id, owner=request.user)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found or you don't have permission."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Lấy tất cả attempts đã submit cho course này
        attempts = Attempt.objects.filter(
            quiz__course=course, 
            submitted=True
        ).select_related('quiz', 'user')
        
        # Tính điểm trung bình
        avg_score = attempts.aggregate(avg=Avg('score'))['avg'] or 0
        total_attempts = attempts.count()
        
        # Phân phối điểm số
        score_dist = []
        score_ranges = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10)]
        for min_score, max_score in score_ranges:
            count = attempts.filter(score__gte=min_score, score__lt=max_score).count()
            if count > 0:
                score_dist.append({
                    'score_range': f"{min_score}-{max_score}",
                    'count': count
                })
        
        # Thống kê skill performance
        questions = Question.objects.filter(quiz__course=course)
        skill_stats = []
        
        # Group questions by skill_tags và tính correct rate
        for question in questions:
            if question.skill_tags:
                for skill in question.skill_tags:
                    # Count total attempts for this skill
                    skill_attempts = attempts.filter(
                        quiz__questions=question
                    ).count()
                    
                    # Count correct attempts (check trong detail JSON)
                    correct_attempts = 0
                    for attempt in attempts.filter(quiz__questions=question):
                        if attempt.detail and 'answers' in attempt.detail:
                            for answer in attempt.detail['answers']:
                                if (answer.get('question_id') == question.id and 
                                    answer.get('correct', False)):
                                    correct_attempts += 1
                    
                    if skill_attempts > 0:
                        skill_stats.append({
                            'skill': skill,
                            'total': skill_attempts,
                            'correct': correct_attempts,
                            'correct_rate': correct_attempts / skill_attempts
                        })
        
        # Câu hỏi "bẫy" - wrong nhiều nhất
        weak_questions = []
        for question in questions:
            wrong_count = 0
            for attempt in attempts.filter(quiz__questions=question):
                if attempt.detail and 'answers' in attempt.detail:
                    for answer in attempt.detail['answers']:
                        if (answer.get('question_id') == question.id and 
                            not answer.get('correct', True)):
                            wrong_count += 1
            
            if wrong_count > 0:
                weak_questions.append({
                    'content': question.content[:100] + '...' if len(question.content) > 100 else question.content,
                    'wrong_count': wrong_count,
                    'difficulty': question.difficulty,
                    'skill_tags': question.skill_tags
                })
        
        # Sort by wrong_count descending
        weak_questions.sort(key=lambda x: x['wrong_count'], reverse=True)
        weak_questions = weak_questions[:5]  # Top 5
        
        data = {
            "avg_score": round(avg_score, 2),
            "total_attempts": total_attempts,
            "score_distribution": score_dist,
            "skill_stats": skill_stats,
            "weak_questions": weak_questions,
            "course_info": {
                "id": course.id,
                "title": course.title,
                "code": course.code
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)


class StudentDashboardAPI(APIView):
    """
    Dashboard cho Student - personal performance & SR reviews
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'student':
            return Response(
                {"detail": "Permission denied. Student role required."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Lấy attempts của student
        attempts = Attempt.objects.filter(
            user=user, 
            submitted=True
        ).select_related('quiz')
        
        avg_score = attempts.aggregate(avg=Avg('score'))['avg'] or 0
        total_attempts = attempts.count()
        
        # Skill performance của student
        skill_stats = []
        questions_answered = []
        
        for attempt in attempts:
            if attempt.detail and 'answers' in attempt.detail:
                for answer in attempt.detail['answers']:
                    try:
                        question = Question.objects.get(id=answer['question_id'])
                        questions_answered.append({
                            'question': question,
                            'correct': answer.get('correct', False)
                        })
                    except Question.DoesNotExist:
                        continue
        
        # Group by skills
        skill_performance = {}
        for qa in questions_answered:
            if qa['question'].skill_tags:
                for skill in qa['question'].skill_tags:
                    if skill not in skill_performance:
                        skill_performance[skill] = {'total': 0, 'correct': 0}
                    skill_performance[skill]['total'] += 1
                    if qa['correct']:
                        skill_performance[skill]['correct'] += 1
        
        for skill, perf in skill_performance.items():
            skill_stats.append({
                'skill': skill,
                'total': perf['total'],
                'correct': perf['correct'],
                'correct_rate': perf['correct'] / perf['total'] if perf['total'] > 0 else 0
            })
        
        # Spaced Repetition reviews due
        reviews_due = AttemptReview.objects.filter(
            user=user, 
            next_review__lte=date.today()
        ).count()
        
        review_list = AttemptReview.objects.filter(
            user=user, 
            next_review__lte=date.today()
        ).select_related('question')[:10]  # Limit 10 cho response size
        
        review_data = []
        for review in review_list:
            review_data.append({
                'question_id': review.question.id,
                'content': review.question.content[:100] + '...' if len(review.question.content) > 100 else review.question.content,
                'next_review': review.next_review,
                'difficulty': review.question.difficulty,
                'skill_tags': review.question.skill_tags,
                'interval': review.interval,
                'repetition': review.repetition
            })
        
        data = {
            "avg_score": round(avg_score, 2),
            "total_attempts": total_attempts,
            "skill_stats": skill_stats,
            "reviews_due": reviews_due,
            "review_list": review_data,
            "user_info": {
                "username": user.username,
                "full_name": user.get_full_name()
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)


class AdminStatsAPI(APIView):
    """
    Admin Statistics - system-wide metrics
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Basic counts
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_quizzes = Quiz.objects.count()
        total_attempts = Attempt.objects.count()
        
        # User growth by month
        try:
            growth_users = User.objects.annotate(
                month=TruncMonth('date_joined')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            
            growth_users_data = [
                {'month': item['month'], 'count': item['count']} 
                for item in growth_users
            ]
        except Exception:
            # Fallback nếu TruncMonth không support (SQLite limitations)
            growth_users_data = []
        
        # Attempt growth by month  
        try:
            growth_attempts = Attempt.objects.annotate(
                month=TruncMonth('start_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            
            growth_attempts_data = [
                {'month': item['month'], 'count': item['count']}
                for item in growth_attempts
            ]
        except Exception:
            # Fallback
            growth_attempts_data = []
        
        # Additional metrics
        active_students = User.objects.filter(
            role='student',
            quiz_attempts__isnull=False
        ).distinct().count()
        
        avg_quiz_score = Attempt.objects.filter(
            submitted=True
        ).aggregate(avg=Avg('score'))['avg'] or 0
        
        data = {
            "total_users": total_users,
            "total_courses": total_courses,
            "total_quizzes": total_quizzes,
            "total_attempts": total_attempts,
            "active_students": active_students,
            "avg_quiz_score": round(avg_quiz_score, 2),
            "growth_users": growth_users_data,
            "growth_attempts": growth_attempts_data,
        }
        
        return Response(data, status=status.HTTP_200_OK)

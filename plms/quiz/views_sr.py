"""
Spaced Repetition API Views
API endpoints cho hệ thống ôn tập ngắt quãng (Spaced Repetition)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from datetime import date
from django.contrib.auth import get_user_model

from quiz.models import AttemptReview, Question
from quiz.sr_utils import sm2, calculate_next_review, update_review_after_attempt
from analytics.serializers import SRReviewSerializer, SRQualityUpdateSerializer

User = get_user_model()


class SRReviewAPI(APIView):
    """
    Spaced Repetition Review API
    GET: Lấy danh sách câu hỏi cần ôn tập hôm nay
    POST: Cập nhật quality score sau khi ôn tập
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Lấy danh sách câu hỏi cần ôn tập
        """
        user = request.user
        limit = request.GET.get('limit', 20)
        
        try:
            limit = int(limit)
            if limit > 50:  # Giới hạn tối đa
                limit = 50
        except (ValueError, TypeError):
            limit = 20
        
        # Lấy reviews cần làm hôm nay
        reviews = AttemptReview.objects.filter(
            user=user, 
            next_review__lte=date.today()
        ).select_related('question').order_by('next_review', 'efactor')[:limit]
        
        review_data = []
        for review in reviews:
            review_data.append({
                'question_id': review.question.id,
                'content': review.question.content,
                'next_review': review.next_review,
                'difficulty': review.question.difficulty,
                'skill_tags': review.question.skill_tags or [],
                'interval': review.interval,
                'repetition': review.repetition,
                'efactor': review.efactor,
                'last_review': review.last_review,
                'options': review.question.options or []
            })
        
        return Response({
            'count': len(review_data),
            'reviews': review_data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Cập nhật quality score sau khi ôn tập một câu hỏi
        """
        serializer = SRQualityUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question_id = serializer.validated_data['question_id']
        quality = serializer.validated_data['quality']
        user = request.user
        
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return Response({
                "detail": "Question not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Lấy hoặc tạo AttemptReview
        review, created = AttemptReview.objects.get_or_create(
            user=user, 
            question=question,
            defaults={
                'next_review': date.today(),
                'quality': quality
            }
        )
        
        # Cập nhật SM-2 algorithm
        review.interval, review.repetition, review.efactor = sm2(
            quality, review.interval, review.repetition, review.efactor
        )
        review.next_review = calculate_next_review(review.interval)
        review.last_review = date.today()
        review.quality = quality
        review.save()
        
        return Response({
            "message": "Review updated successfully",
            "next_review": review.next_review,
            "interval": review.interval,
            "repetition": review.repetition,
            "efactor": round(review.efactor, 2)
        }, status=status.HTTP_200_OK)


class SRStatsAPI(APIView):
    """
    Spaced Repetition Statistics
    Thống kê về việc ôn tập của user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Tổng số câu hỏi đang trong hệ thống SR
        total_reviews = AttemptReview.objects.filter(user=user).count()
        
        # Số câu cần ôn hôm nay
        reviews_due_today = AttemptReview.objects.filter(
            user=user,
            next_review__lte=date.today()
        ).count()
        
        # Số câu quá hạn (overdue)
        overdue_reviews = AttemptReview.objects.filter(
            user=user,
            next_review__lt=date.today()
        ).count()
        
        # Phân phối theo interval
        interval_stats = {}
        reviews = AttemptReview.objects.filter(user=user)
        for review in reviews:
            interval_range = self._get_interval_range(review.interval)
            if interval_range not in interval_stats:
                interval_stats[interval_range] = 0
            interval_stats[interval_range] += 1
        
        # Phân phối theo efactor
        efactor_ranges = [(1.3, 2.0), (2.0, 2.5), (2.5, 3.0), (3.0, 4.0)]
        efactor_stats = {}
        for min_ef, max_ef in efactor_ranges:
            count = reviews.filter(
                efactor__gte=min_ef, 
                efactor__lt=max_ef
            ).count()
            if count > 0:
                efactor_stats[f"{min_ef}-{max_ef}"] = count
        
        # Skill distribution
        skill_stats = {}
        for review in reviews:
            if review.question.skill_tags:
                for skill in review.question.skill_tags:
                    if skill not in skill_stats:
                        skill_stats[skill] = 0
                    skill_stats[skill] += 1
        
        data = {
            "total_reviews": total_reviews,
            "reviews_due_today": reviews_due_today,
            "overdue_reviews": overdue_reviews,
            "interval_distribution": interval_stats,
            "efactor_distribution": efactor_stats,
            "skill_distribution": skill_stats,
            "completion_rate": {
                "total_possible": reviews_due_today,
                "completed_today": 0  # Có thể track riêng nếu cần
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
    
    def _get_interval_range(self, interval):
        """Helper để group intervals vào ranges"""
        if interval == 1:
            return "1 day"
        elif interval <= 7:
            return "2-7 days"
        elif interval <= 30:
            return "1-4 weeks"
        elif interval <= 90:
            return "1-3 months"
        else:
            return "3+ months"


class SRBulkUpdateAPI(APIView):
    """
    Bulk update multiple review qualities
    Useful cho mobile app hoặc batch operations
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Bulk update multiple reviews
        Expected format:
        {
            "reviews": [
                {"question_id": 1, "quality": 4},
                {"question_id": 2, "quality": 2},
                ...
            ]
        }
        """
        reviews_data = request.data.get('reviews', [])
        if not reviews_data or not isinstance(reviews_data, list):
            return Response({
                "detail": "reviews field is required and must be a list"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        results = []
        errors = []
        
        for i, review_data in enumerate(reviews_data):
            try:
                # Validate individual review data
                serializer = SRQualityUpdateSerializer(data=review_data)
                if not serializer.is_valid():
                    errors.append({
                        "index": i,
                        "question_id": review_data.get('question_id'),
                        "errors": serializer.errors
                    })
                    continue
                
                question_id = serializer.validated_data['question_id']
                quality = serializer.validated_data['quality']
                
                # Process the review
                question = Question.objects.get(pk=question_id)
                review = update_review_after_attempt(
                    user=user,
                    question=question,
                    correct=quality >= 3,  # Convert quality to correct/incorrect
                    attempt=None
                )
                
                results.append({
                    "question_id": question_id,
                    "next_review": review.next_review,
                    "interval": review.interval,
                    "success": True
                })
                
            except Question.DoesNotExist:
                errors.append({
                    "index": i,
                    "question_id": review_data.get('question_id'),
                    "errors": {"question_id": ["Question not found"]}
                })
            except Exception as e:
                errors.append({
                    "index": i,
                    "question_id": review_data.get('question_id'),
                    "errors": {"general": [str(e)]}
                })
        
        return Response({
            "results": results,
            "errors": errors,
            "total_processed": len(results),
            "total_errors": len(errors)
        }, status=status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS)

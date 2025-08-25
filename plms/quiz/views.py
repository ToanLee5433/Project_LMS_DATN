from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import Quiz, Question, Attempt
from .serializers import QuizSerializer, QuestionSerializer, AttemptSerializer, AttemptDetailSerializer
from .permissions import IsTeacherOrAdmin, IsQuizOwnerOrAdmin
from .utils import grade_fixed
from lms.models import Enrollment


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Quiz.objects.all()
        course_id = self.request.query_params.get("course_id")
        tags = self.request.query_params.get("tags")

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag)

        return queryset.order_by("-created_at")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsTeacherOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """
        API để lấy danh sách câu hỏi của quiz
        """
        quiz = self.get_object()
        questions = quiz.questions.all().order_by('order')
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Question.objects.all()
        quiz_id = self.request.query_params.get("quiz_id")
        type_filter = self.request.query_params.get("type")
        difficulty = self.request.query_params.get("difficulty")

        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)

        if type_filter:
            queryset = queryset.filter(type=type_filter)

        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        return queryset.order_by("order")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsQuizOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]


class AttemptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Attempt.objects.all()

        # Giáo viên/admin có thể xem tất cả
        if user.role in ["teacher", "admin"]:
            quiz_id = self.request.query_params.get("quiz_id")
            user_id = self.request.query_params.get("user_id")

            if quiz_id:
                queryset = queryset.filter(quiz_id=quiz_id)
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            # Học sinh chỉ xem attempts của mình
            queryset = queryset.filter(user=user)

        return queryset.order_by("-start_at")

    def get_serializer_class(self):
        user = self.request.user
        if user.role in ["teacher", "admin"]:
            return AttemptDetailSerializer
        return AttemptSerializer

    @action(detail=False, methods=["get"])
    def my_attempts(self, request):
        """
        API để học sinh xem attempts của mình
        """
        attempts = Attempt.objects.filter(user=request.user).order_by("-start_at")
        serializer = self.get_serializer(attempts, many=True)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def start_attempt(request):
    """
    API để bắt đầu một attempt mới
    """
    quiz_id = request.data.get("quiz_id")
    
    if not quiz_id:
        return Response(
            {"error": "quiz_id là bắt buộc"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    quiz = get_object_or_404(Quiz, pk=quiz_id)

    # Kiểm tra enrollment
    if not Enrollment.objects.filter(
        user=request.user, 
        course=quiz.course,
        status="active"
    ).exists():
        return Response(
            {"error": "Bạn chưa đăng ký khóa học này"}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # Kiểm tra số lần thử
    user_attempts = Attempt.objects.filter(user=request.user, quiz=quiz).count()
    if quiz.attempts_allowed > 0 and user_attempts >= quiz.attempts_allowed:
        return Response(
            {"error": f"Bạn đã vượt quá số lần thử cho phép ({quiz.attempts_allowed})"}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # Tạo attempt mới
    attempt = Attempt.objects.create(
        quiz=quiz,
        user=request.user,
        start_at=timezone.now(),
    )

    return Response({
        "attempt_id": attempt.id,
        "quiz_title": quiz.title,
        "time_limit": quiz.time_limit,
        "start_at": attempt.start_at,
        "message": "Bắt đầu làm bài thành công!"
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_attempt(request):
    """
    API để nộp bài và chấm điểm
    """
    attempt_id = request.data.get("attempt_id")
    answers = request.data.get("answers", {})
    
    if not attempt_id:
        return Response(
            {"error": "attempt_id là bắt buộc"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    attempt = get_object_or_404(Attempt, pk=attempt_id, user=request.user)

    if attempt.submitted:
        return Response(
            {"error": "Bài thi đã được nộp rồi"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kiểm tra thời gian
    if attempt.quiz.time_limit:
        elapsed = (timezone.now() - attempt.start_at).total_seconds() / 60
        if elapsed > attempt.quiz.time_limit:
            return Response(
                {"error": "Đã hết thời gian làm bài"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # Chấm điểm
    score, detail = grade_fixed(attempt.quiz, answers)
    
    # Cập nhật attempt
    attempt.end_at = timezone.now()
    attempt.score = score
    attempt.detail = detail
    attempt.submitted = True
    attempt.save()

    return Response({
        "attempt_id": attempt.id,
        "score": score,
        "total_points": attempt.quiz.total_points,
        "percentage": round((score / attempt.quiz.total_points) * 100, 2) if attempt.quiz.total_points > 0 else 0,
        "message": "Nộp bài thành công!"
    }, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta

from lms.models import Enrollment
from .models import Quiz, Question, Attempt
from .adaptive import pick_next_question, update_theta
from .sr_utils import update_review_after_attempt


def grade_one(question, given):
    """Chấm điểm một câu hỏi"""
    if question.type == "mcq":
        opts = question.options or []
        
        def in_range(i): 
            return isinstance(i, int) and 0 <= i < len(opts)
        
        key = question.answer_key
        if isinstance(key, list):  # Multiple choice multiple answer
            if not (isinstance(given, list) and all(in_range(i) for i in given)):
                return False, 0
            is_correct = set(given) == set(key)
        else:  # Single choice
            if not in_range(given):
                return False, 0
            is_correct = (given == key)
    else:  # fill-in-the-blank
        if isinstance(question.answer_key, str) and isinstance(given, str):
            is_correct = question.answer_key.strip().casefold() == given.strip().casefold()
        else:
            is_correct = (given == question.answer_key)
    
    pts = question.points if is_correct else 0
    return is_correct, pts


def _get_config(quiz):
    """Lấy cấu hình max/min questions"""
    return quiz.max_questions or 10, quiz.min_questions or 6


def _ensure_enrolled(user, quiz):
    """Kiểm tra user đã enroll course chưa"""
    return Enrollment.objects.filter(
        course=quiz.course, 
        user=user, 
        status="active"
    ).exists()


def _guard_time_limit(att):
    """Kiểm tra thời gian làm bài"""
    tl = att.quiz.time_limit
    if not tl:
        return None
    deadline = att.start_at + timedelta(minutes=tl)
    if timezone.now() > deadline:
        return {"detail": "Đã quá thời gian làm bài."}
    return None


class AdaptiveStartAPI(APIView):
    """Khởi tạo adaptive quiz attempt và trả câu đầu tiên"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, quiz_id):
        user = request.user
        quiz = get_object_or_404(
            Quiz.objects.select_related("course").prefetch_related("questions"),
            pk=quiz_id
        )
        
        # Validate adaptive strategy
        if quiz.strategy != "adaptive":
            return Response(
                {"detail": "Quiz không phải adaptive."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check enrollment (except for teacher/admin)
        if not _ensure_enrolled(user, quiz) and user.role not in ("teacher", "admin"):
            return Response(
                {"detail": "Bạn chưa ghi danh khóa học này."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create new attempt
        att = Attempt.objects.create(
            quiz=quiz,
            user=user,
            ability_estimate=0.5,
            detail={
                "answers": [],
                "asked_ids": [],
                "raw_score": 0
            }
        )
        
        # Pick first question
        first_q = pick_next_question(quiz.questions.all(), set(), att.ability_estimate or 0.5)
        if not first_q:
            return Response(
                {"detail": "Không còn câu hỏi."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save first question to asked_ids
        att.detail["asked_ids"].append(first_q.id)
        att.save(update_fields=["detail"])
        
        question_data = {
            "question_id": first_q.id,
            "type": first_q.type,
            "content": first_q.content,
            "options": first_q.options,
            "order": first_q.order,
            "difficulty": first_q.difficulty
        }
        
        return Response({
            "attempt_id": att.id,
            "question": question_data
        }, status=status.HTTP_201_CREATED)


class AdaptiveAnswerAPI(APIView):
    """Nộp đáp án, cập nhật ability, trả câu tiếp theo"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, attempt_id):
        att = get_object_or_404(
            Attempt.objects.select_related("quiz").prefetch_related("quiz__questions"),
            pk=attempt_id,
            user=request.user
        )
        
        # Check if already submitted
        if att.submitted:
            return Response(
                {"detail": "Attempt đã kết thúc."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check time limit
        guard = _guard_time_limit(att)
        if guard:
            return Response(guard, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate input
        qid = request.data.get("question_id")
        given = request.data.get("given")
        
        if qid is None:
            return Response(
                {"detail": "Thiếu question_id."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get questions and validate
        asked_ids = set(att.detail.get("asked_ids", []))
        questions_dict = {q.id: q for q in att.quiz.questions.all()}
        
        if qid not in questions_dict:
            return Response(
                {"detail": "question_id không thuộc quiz."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if qid not in asked_ids:
            return Response(
                {"detail": "Câu này chưa được phát ra trong attempt."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already answered
        answers = att.detail.get("answers", [])
        if any(a["qid"] == qid for a in answers):
            return Response(
                {"detail": "Câu này đã được chấm rồi."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Grade the answer
        question = questions_dict[qid]
        is_correct, pts = grade_one(question, given)
        
        # Update ability
        theta_old = att.ability_estimate or 0.5
        theta_new = update_theta(theta_old, question.difficulty or 0.5, is_correct)
        
        # Save answer result
        answers.append({
            "qid": question.id,
            "given": given,
            "correct": is_correct,
            "points": pts,
            "theta": round(theta_new, 4),
            "difficulty": question.difficulty
        })
        
        att.detail["answers"] = answers
        att.detail["raw_score"] = int(att.detail.get("raw_score", 0) + pts)
        att.ability_estimate = theta_new
        att.save(update_fields=["detail", "ability_estimate"])
        
        # Check termination conditions
        max_q, min_q = _get_config(att.quiz)
        
        # Early convergence stop
        eps = 0.01
        if (len(answers) >= min_q and len(answers) >= 2 and 
            abs(answers[-1]["theta"] - answers[-2]["theta"]) < eps):
            return Response({
                "done": True,
                "ability": round(theta_new, 4),
                "score_so_far": att.detail["raw_score"],
                "reason": "converged"
            })
        
        # Max questions reached
        if len(answers) >= max_q:
            return Response({
                "done": True,
                "ability": round(theta_new, 4),
                "score_so_far": att.detail["raw_score"]
            })
        
        # Pick next question
        next_q = pick_next_question(att.quiz.questions.all(), asked_ids, theta_new)
        if not next_q:
            return Response({
                "done": True,
                "ability": round(theta_new, 4),
                "score_so_far": att.detail["raw_score"]
            })
        
        # Save next question to asked_ids
        att.detail["asked_ids"].append(next_q.id)
        att.save(update_fields=["detail"])
        
        next_question_data = {
            "question_id": next_q.id,
            "type": next_q.type,
            "content": next_q.content,
            "options": next_q.options,
            "order": next_q.order,
            "difficulty": next_q.difficulty
        }
        
        return Response({
            "done": False,
            "ability": round(theta_new, 4),
            "next_question": next_question_data
        })


class AdaptiveFinishAPI(APIView):
    """Kết thúc attempt, trả kết quả chi tiết"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, attempt_id):
        att = get_object_or_404(
            Attempt.objects.select_related("quiz"),
            pk=attempt_id,
            user=request.user
        )
        
        if att.submitted:
            return Response(
                {"detail": "Attempt đã kết thúc."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check time limit
        guard = _guard_time_limit(att)
        if guard:
            return Response(guard, status=status.HTTP_400_BAD_REQUEST)
        
        # Check minimum questions
        answers = att.detail.get("answers", [])
        max_q, min_q = _get_config(att.quiz)
        
        if len(answers) < min_q:
            return Response(
                {"detail": f"Bạn phải trả lời ít nhất {min_q} câu trước khi kết thúc."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Finalize attempt
        score = att.detail.get("raw_score", 0)
        att.score = float(score)
        att.submitted = True
        att.end_at = timezone.now()
        att.save(update_fields=["score", "submitted", "end_at"])
        
        # Tích hợp Spaced Repetition cho adaptive quiz
        try:
            if answers:
                for answer_data in answers:
                    try:
                        question = Question.objects.get(id=answer_data['question_id'])
                        correct = answer_data.get('correct', False)
                        
                        # Tự động tạo/cập nhật AttemptReview
                        update_review_after_attempt(
                            user=request.user,
                            question=question,
                            correct=correct,
                            attempt=att
                        )
                    except Question.DoesNotExist:
                        continue
        except Exception as e:
            # Log error nhưng không fail
            print(f"SR Integration error in adaptive finish: {e}")
        
        return Response({
            "attempt_id": att.id,
            "score": score,
            "ability": round(att.ability_estimate or 0.5, 4),
            "questions_answered": len(answers),
            "answers": answers,
            "sr_enabled": True
        })


class AdaptiveStatusAPI(APIView):
    """Xem trạng thái attempt (để resume hoặc debug)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, attempt_id):
        att = get_object_or_404(
            Attempt.objects.select_related("quiz"),
            pk=attempt_id,
            user=request.user
        )
        
        detail = att.detail or {}
        asked_ids = detail.get("asked_ids", [])
        answers = detail.get("answers", [])
        
        return Response({
            "attempt_id": att.id,
            "quiz_id": att.quiz_id,
            "submitted": att.submitted,
            "ability": round(att.ability_estimate or 0.5, 4),
            "asked_ids": asked_ids,
            "answered": len(answers),
            "score_so_far": detail.get("raw_score", 0),
            "time_limit": att.quiz.time_limit,
            "start_at": att.start_at,
            "end_at": att.end_at
        })

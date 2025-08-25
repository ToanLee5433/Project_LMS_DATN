from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    QuizViewSet, 
    QuestionViewSet, 
    AttemptViewSet, 
    start_attempt, 
    submit_attempt
)
from .views_adaptive import (
    AdaptiveStartAPI,
    AdaptiveAnswerAPI, 
    AdaptiveFinishAPI,
    AdaptiveStatusAPI
)

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'attempts', AttemptViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('start-attempt/', start_attempt, name='start-attempt'),
    path('submit-attempt/', submit_attempt, name='submit-attempt'),
    
    # Adaptive Quiz endpoints
    path('quizzes/<int:quiz_id>/adaptive/start/', AdaptiveStartAPI.as_view(), name='adaptive_start'),
    path('adaptive/<int:attempt_id>/answer/', AdaptiveAnswerAPI.as_view(), name='adaptive_answer'),
    path('adaptive/<int:attempt_id>/finish/', AdaptiveFinishAPI.as_view(), name='adaptive_finish'),
    path('adaptive/<int:attempt_id>/status/', AdaptiveStatusAPI.as_view(), name='adaptive_status'),
]

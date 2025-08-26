"""
Analytics Serializers for DRF API responses
"""
from rest_framework import serializers


class ScoreDistributionSerializer(serializers.Serializer):
    """Serializer for score distribution data"""
    score = serializers.FloatField()
    count = serializers.IntegerField()


class WeakQuestionSerializer(serializers.Serializer):
    """Serializer for weak/problematic questions"""
    content = serializers.CharField()
    wrong_count = serializers.IntegerField()
    difficulty = serializers.FloatField(required=False)
    skill_tags = serializers.ListField(child=serializers.CharField(), required=False)


class SkillStatsSerializer(serializers.Serializer):
    """Serializer for skill performance statistics"""
    skill_tags = serializers.ListField(child=serializers.CharField())
    total = serializers.IntegerField()
    correct = serializers.IntegerField()
    correct_rate = serializers.FloatField()


class UserGrowthSerializer(serializers.Serializer):
    """Serializer for user growth data"""
    month = serializers.DateField()
    count = serializers.IntegerField()


class AttemptGrowthSerializer(serializers.Serializer):
    """Serializer for attempt growth data"""
    month = serializers.DateField()
    count = serializers.IntegerField()


class TeacherAnalyticsSerializer(serializers.Serializer):
    """Serializer for teacher course analytics"""
    avg_score = serializers.FloatField()
    total_attempts = serializers.IntegerField()
    score_distribution = ScoreDistributionSerializer(many=True)
    skill_stats = SkillStatsSerializer(many=True)
    weak_questions = WeakQuestionSerializer(many=True)


class StudentDashboardSerializer(serializers.Serializer):
    """Serializer for student dashboard"""
    avg_score = serializers.FloatField()
    total_attempts = serializers.IntegerField()
    skill_stats = SkillStatsSerializer(many=True)
    reviews_due = serializers.IntegerField()
    review_list = serializers.ListField(child=serializers.DictField())


class AdminStatsSerializer(serializers.Serializer):
    """Serializer for admin statistics"""
    total_users = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_quizzes = serializers.IntegerField()
    total_attempts = serializers.IntegerField()
    growth_users = UserGrowthSerializer(many=True)
    growth_attempts = AttemptGrowthSerializer(many=True)


class SRReviewSerializer(serializers.Serializer):
    """Serializer for Spaced Repetition reviews"""
    question_id = serializers.IntegerField()
    content = serializers.CharField()
    next_review = serializers.DateField()
    difficulty = serializers.FloatField(required=False)
    skill_tags = serializers.ListField(child=serializers.CharField(), required=False)
    interval = serializers.IntegerField(required=False)
    repetition = serializers.IntegerField(required=False)
    efactor = serializers.FloatField(required=False)


class SRQualityUpdateSerializer(serializers.Serializer):
    """Serializer for updating SR quality"""
    question_id = serializers.IntegerField()
    quality = serializers.IntegerField(min_value=0, max_value=5)
    
    def validate_quality(self, value):
        if not (0 <= value <= 5):
            raise serializers.ValidationError("Quality must be between 0 and 5")
        return value

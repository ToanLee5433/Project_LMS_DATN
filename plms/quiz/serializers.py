from rest_framework import serializers
from .models import Quiz, Question, Attempt


class QuestionSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "quiz",
            "quiz_title", 
            "type",
            "content",
            "options",
            "answer_key",
            "skill_tags",
            "difficulty",
            "points",
            "order",
        ]

    def validate(self, data):
        """
        Validate question data based on type
        """
        question_type = data.get("type")
        
        if question_type == "mcq":
            options = data.get("options", [])
            answer_key = data.get("answer_key")
            
            # MCQ must have at least 2 options
            if len(options) < 2:
                raise serializers.ValidationError({
                    "options": "MCQ cần ít nhất 2 lựa chọn"
                })
            
            # Check if answer_key index is valid
            def is_valid_index(index):
                return isinstance(index, int) and 0 <= index < len(options)
            
            if isinstance(answer_key, int) and not is_valid_index(answer_key):
                raise serializers.ValidationError({
                    "answer_key": "Index đáp án không hợp lệ"
                })
            
            if isinstance(answer_key, list) and not all(
                is_valid_index(i) for i in answer_key
            ):
                raise serializers.ValidationError({
                    "answer_key": "Danh sách đáp án không hợp lệ"
                })
        
        return data


class QuizSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    question_count = serializers.IntegerField(
        source="questions.count", read_only=True
    )

    class Meta:
        model = Quiz
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "description",
            "time_limit",
            "attempts_allowed",
            "total_points",
            "strategy",
            "max_questions",
            "min_questions",
            "tags",
            "created_at",
            "owner",
            "owner_name",
            "question_count",
        ]
        read_only_fields = ["owner", "total_points", "created_at"]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Validate max_questions >= min_questions"""
        max_q = data.get("max_questions", getattr(self.instance, "max_questions", 10))
        min_q = data.get("min_questions", getattr(self.instance, "min_questions", 6))
        if min_q and max_q and min_q > max_q:
            raise serializers.ValidationError({
                "min_questions": "Phải ≤ max_questions."
            })
        return data


class AttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "quiz",
            "quiz_title",
            "user",
            "user_name",
            "start_at",
            "end_at",
            "score",
            "ability_estimate",
            "detail",
            "submitted",
        ]
        read_only_fields = [
            "user",
            "score",
            "submitted",
            "detail",
            "start_at",
            "end_at",
            "ability_estimate",
        ]


class AttemptDetailSerializer(serializers.ModelSerializer):
    """
    Serializer với thông tin chi tiết cho teacher/admin
    """
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    max_score = serializers.IntegerField(source="quiz.total_points", read_only=True)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "quiz",
            "quiz_title",
            "user",
            "user_name",
            "start_at",
            "end_at",
            "score",
            "max_score",
            "ability_estimate",
            "detail",
            "submitted",
        ]

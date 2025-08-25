def grade_fixed(quiz, answers_map):
    """
    Hàm chấm điểm cho quiz fixed strategy.
    
    Args:
        quiz: Quiz instance
        answers_map: Dict với key là question_id (string), value là câu trả lời
        
    Returns:
        tuple: (total_score, details_list)
    """
    details = []
    score = 0
    
    for question in quiz.questions.all():
        given_answer = answers_map.get(str(question.id))
        correct = False
        
        if question.type == "mcq":
            answer_key = question.answer_key
            if isinstance(answer_key, list):
                # Multiple correct answers
                correct = (
                    isinstance(given_answer, list)
                    and set(given_answer) == set(answer_key)
                )
            else:
                # Single correct answer
                correct = (given_answer == answer_key)
        else:  # fill type
            if isinstance(given_answer, str) and isinstance(question.answer_key, str):
                # Case-insensitive string comparison
                correct = (
                    question.answer_key.strip().lower()
                    == given_answer.strip().lower()
                )
            else:
                # Exact match for numbers or other types
                correct = (given_answer == question.answer_key)
        
        points_earned = question.points if correct else 0
        score += points_earned
        
        details.append({
            "question_id": question.id,
            "given": given_answer,
            "correct": correct,
            "points": points_earned,
            "max_points": question.points
        })
    
    return score, details

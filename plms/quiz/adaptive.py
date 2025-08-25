import math
import random

ALPHA = 4.0   # độ dốc logistic
K = 0.18      # hệ số cập nhật

def sigmoid(x: float) -> float:
    """Hàm sigmoid để tính xác suất"""
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0

def expected_correct(theta: float, difficulty: float) -> float:
    """Tính xác suất đúng kỳ vọng dựa trên ability và difficulty"""
    return sigmoid(ALPHA * (theta - difficulty))

def update_theta(theta: float, difficulty: float, is_correct: bool) -> float:
    """Cập nhật ability estimate theo mô hình ELO-like"""
    exp_corr = expected_correct(theta, difficulty)
    actual = 1.0 if is_correct else 0.0
    new_theta = theta + K * (actual - exp_corr)
    return max(0.0, min(1.0, new_theta))

def pick_next_question(questions, asked_qids, theta: float):
    """
    Chọn câu hỏi tiếp theo có difficulty gần với ability nhất
    questions: Iterable[Question] (đã Prefetch)
    asked_qids: set[int] các question_id đã hỏi
    theta: ability hiện tại
    Trả về Question có |difficulty - theta| nhỏ nhất (chưa hỏi)
    """
    candidates = [q for q in questions if q.id not in asked_qids]
    if not candidates:
        return None
    
    # Sắp xếp theo độ gần với ability
    candidates.sort(key=lambda q: abs((q.difficulty or 0.5) - theta))
    
    # Tie-break: chọn ngẫu nhiên trong các câu có độ gần tương đương
    best_dist = abs((candidates[0].difficulty or 0.5) - theta)
    eps = 1e-6
    top_candidates = [
        q for q in candidates 
        if abs((q.difficulty or 0.5) - theta) - best_dist <= eps
    ]
    
    return random.choice(top_candidates)

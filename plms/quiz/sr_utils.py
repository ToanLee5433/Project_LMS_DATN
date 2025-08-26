"""
Spaced Repetition Utils - SM-2 Algorithm Implementation
Thuật toán SM-2 variant để tính toán lịch ôn tập
"""
import datetime


def sm2(quality, prev_interval=1, prev_repetition=0, prev_efactor=2.5):
    """
    SM-2 Algorithm for Spaced Repetition
    
    Args:
        quality: 0..5 
            5: hoàn hảo, 
            4: đúng nhưng do dự, 
            3: đúng nhưng khó nhớ, 
            2: sai nhưng gần, 
            1: sai, 
            0: quên hoàn toàn
        prev_interval: khoảng thời gian trước (ngày)
        prev_repetition: số lần lặp trước
        prev_efactor: ease factor trước
    
    Returns:
        tuple: (interval, repetition, efactor)
    """
    if quality < 3:
        # Nếu chất lượng kém, reset về đầu
        repetition = 0
        interval = 1
    else:
        # Tăng số lần lặp
        repetition = prev_repetition + 1
        
        if repetition == 1:
            interval = 1
        elif repetition == 2:
            interval = 6
        else:
            # Tính interval dựa trên efactor
            interval = round(prev_interval * prev_efactor)
    
    # Cập nhật ease factor dựa trên quality
    efactor = prev_efactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    efactor = max(efactor, 1.3)  # Minimum efactor
    
    return interval, repetition, efactor


def calculate_next_review(interval):
    """
    Tính ngày ôn tập tiếp theo
    
    Args:
        interval: số ngày từ hôm nay
    
    Returns:
        datetime.date: ngày ôn tập tiếp theo
    """
    return datetime.date.today() + datetime.timedelta(days=interval)


def map_quality_from_attempt(correct, time_taken=None, time_limit=None, difficulty=None):
    """
    Map từ kết quả attempt sang quality 0-5
    Có thể mở rộng với thời gian và độ khó
    
    Args:
        correct: True/False - đúng/sai
        time_taken: thời gian làm (seconds) - optional
        time_limit: thời gian giới hạn (seconds) - optional  
        difficulty: độ khó câu hỏi 0-1 - optional
    
    Returns:
        int: quality score 0-5
    """
    if correct:
        # Nếu đúng, xét thời gian để đánh giá chất lượng
        if time_taken and time_limit:
            if time_taken < time_limit * 0.3:
                return 5  # Hoàn hảo, rất nhanh
            elif time_taken < time_limit * 0.6:
                return 4  # Đúng và nhanh
            else:
                return 3  # Đúng nhưng chậm/do dự
        else:
            # Không có thông tin thời gian
            return 4  # Đúng nhưng có thể do dự
    else:
        # Nếu sai, có thể xét difficulty để đánh giá
        if difficulty and difficulty > 0.7:
            return 2  # Sai nhưng câu khó, gần đúng
        else:
            return 1  # Sai


def get_reviews_due(user, limit=None):
    """
    Lấy danh sách câu hỏi cần ôn tập hôm nay
    
    Args:
        user: User object
        limit: giới hạn số câu (optional)
    
    Returns:
        QuerySet: AttemptReview objects
    """
    from .models import AttemptReview
    
    reviews = AttemptReview.objects.filter(
        user=user,
        next_review__lte=datetime.date.today()
    ).order_by('next_review', 'efactor')  # Ưu tiên câu quá hạn và khó nhớ
    
    if limit:
        reviews = reviews[:limit]
        
    return reviews


def update_review_after_attempt(user, question, correct, attempt=None, time_taken=None, time_limit=None):
    """
    Tự động cập nhật AttemptReview sau khi làm bài
    
    Args:
        user: User object
        question: Question object  
        correct: True/False
        attempt: Attempt object (optional)
        time_taken: thời gian làm (optional)
        time_limit: thời gian giới hạn (optional)
    
    Returns:
        AttemptReview: updated review object
    """
    from .models import AttemptReview
    
    # Map quality từ kết quả
    quality = map_quality_from_attempt(correct, time_taken, time_limit, question.difficulty)
    
    # Lấy hoặc tạo AttemptReview
    review, created = AttemptReview.objects.get_or_create(
        user=user, 
        question=question,
        defaults={
            'attempt': attempt,
            'quality': quality,
            'next_review': datetime.date.today()
        }
    )
    
    if not created:
        # Cập nhật existing review
        review.quality = quality
        if attempt:
            review.attempt = attempt
            
        # Áp dụng SM-2
        review.interval, review.repetition, review.efactor = sm2(
            quality, review.interval, review.repetition, review.efactor
        )
        review.next_review = calculate_next_review(review.interval)
        review.last_review = datetime.date.today()
        review.save()
    
    return review

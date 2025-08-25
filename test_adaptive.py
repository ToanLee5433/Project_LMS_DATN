"""
Test script for adaptive quiz algorithms
"""
import os
import sys
import django

# Setup Django
sys.path.append('E:/Project_LMS_daTN/plms')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plms.settings')
django.setup()

from quiz.adaptive import update_theta, pick_next_question, expected_correct


def test_algorithms():
    """Test adaptive quiz algorithms"""
    print("🧪 Testing Adaptive Quiz Algorithms")
    print("=" * 50)
    
    # Test 1: Expected Correct Probability
    print("\n📊 Test 1: Expected Correct Probability")
    theta = 0.5
    difficulty = 0.3
    prob = expected_correct(theta, difficulty)
    print(f"  Ability: {theta}, Difficulty: {difficulty}")
    print(f"  Expected Correct Probability: {prob:.4f}")
    assert 0 <= prob <= 1, "Probability should be between 0 and 1"
    assert prob > 0.5, "Higher ability vs lower difficulty should have >50% chance"
    print("  ✅ Expected correct probability test passed")
    
    # Test 2: Theta Update (Correct Answer)
    print("\n📈 Test 2: Theta Update - Correct Answer")
    initial_theta = 0.5
    difficulty = 0.7
    new_theta = update_theta(initial_theta, difficulty, True)
    print(f"  Initial: {initial_theta}, Difficulty: {difficulty}, Correct: True")
    print(f"  New Theta: {new_theta:.4f}")
    assert new_theta > initial_theta, "Correct answer should increase theta"
    assert 0 <= new_theta <= 1, "Theta should stay in bounds"
    print("  ✅ Correct answer theta update test passed")
    
    # Test 3: Theta Update (Wrong Answer)
    print("\n📉 Test 3: Theta Update - Wrong Answer")
    initial_theta = 0.7
    difficulty = 0.3
    new_theta = update_theta(initial_theta, difficulty, False)
    print(f"  Initial: {initial_theta}, Difficulty: {difficulty}, Correct: False")
    print(f"  New Theta: {new_theta:.4f}")
    assert new_theta < initial_theta, "Wrong answer should decrease theta"
    assert 0 <= new_theta <= 1, "Theta should stay in bounds"
    print("  ✅ Wrong answer theta update test passed")
    
    # Test 4: Boundary Conditions
    print("\n🚧 Test 4: Boundary Conditions")
    # High theta, easy question, wrong answer
    high_theta = update_theta(0.95, 0.1, False)
    print(f"  High theta (0.95) + easy (0.1) + wrong = {high_theta:.4f}")
    assert high_theta <= 1.0, "Should not exceed 1.0"
    
    # Low theta, hard question, correct answer
    low_theta = update_theta(0.05, 0.9, True)
    print(f"  Low theta (0.05) + hard (0.9) + correct = {low_theta:.4f}")
    assert low_theta >= 0.0, "Should not go below 0.0"
    print("  ✅ Boundary conditions test passed")
    
    print("\n🎯 Test 5: Mock Question Selection")
    # Create mock questions
    class MockQuestion:
        def __init__(self, id, difficulty):
            self.id = id
            self.difficulty = difficulty
    
    questions = [
        MockQuestion(1, 0.2),
        MockQuestion(2, 0.5),
        MockQuestion(3, 0.8),
        MockQuestion(4, 0.6)
    ]
    
    asked_qids = {1}  # Already asked question 1
    theta = 0.55
    
    # Should pick question closest to theta (0.55)
    # Available: Q2(0.5), Q3(0.8), Q4(0.6)
    # Distances: |0.5-0.55|=0.05, |0.8-0.55|=0.25, |0.6-0.55|=0.05
    # Should pick Q2 or Q4 (tie-break random)
    
    next_q = pick_next_question(questions, asked_qids, theta)
    print(f"  Theta: {theta}, Asked: {asked_qids}")
    print(f"  Available questions: Q2(0.5), Q3(0.8), Q4(0.6)")
    print(f"  Selected: Q{next_q.id} (difficulty: {next_q.difficulty})")
    
    assert next_q.id != 1, "Should not select already asked question"
    assert next_q.id in [2, 4], "Should select question closest to theta"
    print("  ✅ Question selection test passed")
    
    print("\n🎉 All tests passed successfully!")
    return True


if __name__ == "__main__":
    try:
        test_algorithms()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""
End-to-end test script for Adaptive Quiz API
"""
import requests
import json
import time


def test_adaptive_quiz_api():
    """Test complete adaptive quiz flow"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔐 Testing Adaptive Quiz API")
    print("=" * 50)
    
    # Step 1: Login
    print("\n📋 Step 1: Login")
    login_url = f"{base_url}/api/auth/login/"
    login_data = {
        "username": "sv01",
        "password": "Abcd1234!"
    }
    
    try:
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code == 200:
            token = login_response.json()["access"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"  ✅ Login successful")
        else:
            print(f"  ❌ Login failed: {login_response.status_code}")
            print(f"  Response: {login_response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Login error: {e}")
        return False
    
    # Step 2: Start adaptive quiz
    print("\n🚀 Step 2: Start Adaptive Quiz")
    start_url = f"{base_url}/api/quiz/quizzes/3/adaptive/start/"
    
    try:
        start_response = requests.post(start_url, headers=headers)
        if start_response.status_code == 201:
            start_data = start_response.json()
            attempt_id = start_data["attempt_id"]
            question = start_data["question"]
            print(f"  ✅ Quiz started successfully")
            print(f"  Attempt ID: {attempt_id}")
            print(f"  First Question: {question['content']}")
            print(f"  Difficulty: {question['difficulty']}")
        else:
            print(f"  ❌ Start failed: {start_response.status_code}")
            print(f"  Response: {start_response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Start error: {e}")
        return False
    
    # Step 3: Answer questions
    print("\n💭 Step 3: Answer Questions")
    
    for i in range(5):  # Answer up to 5 questions
        question_id = question["question_id"]
        q_type = question["type"]
        
        print(f"\n  Question {i+1}: {question['content'][:50]}...")
        print(f"  Type: {q_type}, Difficulty: {question['difficulty']}")
        
        # Prepare answer based on question type
        if q_type == "mcq":
            # For demo, let's answer based on question content
            if "LIFO" in question["content"]:
                given = 1  # Stack
            elif "Binary" in question["content"]:
                given = 1  # Sorted array
            elif "quicksort" in question["content"]:
                given = 1  # O(n log n)
            else:
                given = 0  # Default first option
        else:  # fill-in-the-blank
            if "FIFO" in question["content"]:
                given = "FIFO"
            elif "heap" in question["content"].lower():
                given = "heap"
            elif "binary tree" in question["content"].lower():
                given = "binary tree"
            else:
                given = "unknown"
        
        # Submit answer
        answer_url = f"{base_url}/api/quiz/adaptive/{attempt_id}/answer/"
        answer_data = {
            "question_id": question_id,
            "given": given
        }
        
        try:
            answer_response = requests.post(answer_url, json=answer_data, headers=headers)
            if answer_response.status_code == 200:
                answer_result = answer_response.json()
                print(f"  📝 Answer submitted: {given}")
                print(f"  🎯 Updated ability: {answer_result['ability']}")
                
                if answer_result.get("done"):
                    print(f"  🏁 Quiz completed! Final score: {answer_result.get('score_so_far', 0)}")
                    if "reason" in answer_result:
                        print(f"  📊 Reason: {answer_result['reason']}")
                    break
                else:
                    question = answer_result["next_question"]
                    print(f"  ➡️ Next question loaded")
            else:
                print(f"  ❌ Answer failed: {answer_response.status_code}")
                print(f"  Response: {answer_response.text}")
                break
        except Exception as e:
            print(f"  ❌ Answer error: {e}")
            break
    
    # Step 4: Check status
    print(f"\n📊 Step 4: Check Status")
    status_url = f"{base_url}/api/quiz/adaptive/{attempt_id}/status/"
    
    try:
        status_response = requests.get(status_url, headers=headers)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"  ✅ Status retrieved")
            print(f"  Submitted: {status_data['submitted']}")
            print(f"  Questions answered: {status_data['answered']}")
            print(f"  Final ability: {status_data['ability']}")
            print(f"  Score so far: {status_data['score_so_far']}")
        else:
            print(f"  ❌ Status failed: {status_response.status_code}")
    except Exception as e:
        print(f"  ❌ Status error: {e}")
    
    # Step 5: Finish (if not already done)
    if not answer_result.get("done"):
        print(f"\n🏁 Step 5: Finish Quiz")
        finish_url = f"{base_url}/api/quiz/adaptive/{attempt_id}/finish/"
        
        try:
            finish_response = requests.post(finish_url, headers=headers)
            if finish_response.status_code == 200:
                finish_data = finish_response.json()
                print(f"  ✅ Quiz finished successfully")
                print(f"  Final score: {finish_data['score']}")
                print(f"  Final ability: {finish_data['ability']}")
                print(f"  Questions answered: {finish_data['questions_answered']}")
            else:
                print(f"  ❌ Finish failed: {finish_response.status_code}")
                print(f"  Response: {finish_response.text}")
        except Exception as e:
            print(f"  ❌ Finish error: {e}")
    
    print(f"\n🎉 Adaptive Quiz API Test Complete!")
    return True


if __name__ == "__main__":
    test_adaptive_quiz_api()

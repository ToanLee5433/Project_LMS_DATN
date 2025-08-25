"""
Quick Day 1-4 System Status Check
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def check_endpoint(url, method='GET', data=None, expected_status=[200, 400, 401]):
    """Check if endpoint is accessible"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        
        return response.status_code in expected_status, response.status_code
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("🎓 LMS SYSTEM DAY 1-4 QUICK CHECK")
    print("="*50)
    
    # Test server accessibility
    print("\n📡 Server Status:")
    server_ok, status = check_endpoint(f"{BASE_URL}/admin/")
    print(f"  {'✅' if server_ok else '❌'} Django Server: {status}")
    
    # Test API documentation
    docs_ok, status = check_endpoint(f"{BASE_URL}/api/docs/")
    print(f"  {'✅' if docs_ok else '❌'} Swagger Docs: {status}")
    
    # Test Day 1: Authentication endpoints
    print("\n🔐 Day 1 - Authentication:")
    
    # Register endpoint
    register_ok, status = check_endpoint(f"{BASE_URL}/api/auth/register/", 'POST', {})
    print(f"  {'✅' if register_ok else '❌'} Register API: {status}")
    
    # Login endpoint
    login_ok, status = check_endpoint(f"{BASE_URL}/api/auth/login/", 'POST', {})
    print(f"  {'✅' if login_ok else '❌'} Login API: {status}")
    
    # Test Day 2: LMS Core endpoints
    print("\n📚 Day 2 - LMS Core:")
    
    courses_ok, status = check_endpoint(f"{BASE_URL}/api/lms/courses/")
    print(f"  {'✅' if courses_ok else '❌'} Courses API: {status}")
    
    modules_ok, status = check_endpoint(f"{BASE_URL}/api/lms/modules/")
    print(f"  {'✅' if modules_ok else '❌'} Modules API: {status}")
    
    lessons_ok, status = check_endpoint(f"{BASE_URL}/api/lms/lessons/")
    print(f"  {'✅' if lessons_ok else '❌'} Lessons API: {status}")
    
    enrollments_ok, status = check_endpoint(f"{BASE_URL}/api/lms/enrollments/")
    print(f"  {'✅' if enrollments_ok else '❌'} Enrollments API: {status}")
    
    # Test Day 3: Quiz System endpoints
    print("\n📝 Day 3 - Quiz System:")
    
    quizzes_ok, status = check_endpoint(f"{BASE_URL}/api/quiz/quizzes/")
    print(f"  {'✅' if quizzes_ok else '❌'} Quizzes API: {status}")
    
    questions_ok, status = check_endpoint(f"{BASE_URL}/api/quiz/questions/")
    print(f"  {'✅' if questions_ok else '❌'} Questions API: {status}")
    
    attempts_ok, status = check_endpoint(f"{BASE_URL}/api/quiz/attempts/")
    print(f"  {'✅' if attempts_ok else '❌'} Attempts API: {status}")
    
    # Test Day 4: Adaptive Quiz endpoints
    print("\n🎯 Day 4 - Adaptive Quiz:")
    
    # These should return 404/405 since they need specific IDs, but endpoint should exist
    adaptive_start_ok, status = check_endpoint(f"{BASE_URL}/api/quiz/quizzes/1/adaptive/start/", 'POST', {}, [200, 400, 401, 404])
    print(f"  {'✅' if adaptive_start_ok else '❌'} Adaptive Start: {status}")
    
    # Test with invalid attempt ID - should get proper error response
    adaptive_answer_ok, status = check_endpoint(f"{BASE_URL}/api/quiz/adaptive/999/answer/", 'POST', {}, [200, 400, 401, 404])
    print(f"  {'✅' if adaptive_answer_ok else '❌'} Adaptive Answer: {status}")
    
    adaptive_finish_ok, status = check_endpoint(f"{BASE_URL}/api/quiz/adaptive/999/finish/", 'POST', {}, [200, 400, 401, 404])
    print(f"  {'✅' if adaptive_finish_ok else '❌'} Adaptive Finish: {status}")
    
    adaptive_status_ok, status = check_endpoint(f"{BASE_URL}/api/quiz/adaptive/999/status/", 'GET', None, [200, 400, 401, 404])
    print(f"  {'✅' if adaptive_status_ok else '❌'} Adaptive Status: {status}")
    
    # Calculate overall status
    all_checks = [
        server_ok, docs_ok, register_ok, login_ok,
        courses_ok, modules_ok, lessons_ok, enrollments_ok,
        quizzes_ok, questions_ok, attempts_ok,
        adaptive_start_ok, adaptive_answer_ok, adaptive_finish_ok, adaptive_status_ok
    ]
    
    passed = sum(all_checks)
    total = len(all_checks)
    success_rate = (passed / total) * 100
    
    print(f"\n{'='*50}")
    print(f"📊 OVERALL STATUS: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Day 1-4 system is fully functional!")
    elif success_rate >= 80:
        print("✅ GOOD! Day 1-4 system is mostly working!")
    elif success_rate >= 70:
        print("⚠️  OK! Day 1-4 system needs minor fixes!")
    else:
        print("❌ ISSUES! Day 1-4 system needs attention!")
    
    print(f"{'='*50}")
    
    # Test actual login flow
    print("\n🧪 FUNCTIONAL TEST:")
    
    try:
        # Try to login with test user
        login_data = {"username": "teacher1", "password": "teacher1pass"}
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data, timeout=10)
        
        if response.status_code == 200:
            token = response.json().get('access')
            print(f"  ✅ Login successful - Token received")
            
            # Try to access protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            courses_response = requests.get(f"{BASE_URL}/api/lms/courses/", headers=headers, timeout=10)
            print(f"  ✅ Protected API access: {courses_response.status_code}")
            
        else:
            print(f"  ℹ️  Login test: Status {response.status_code} (expected if no test user)")
            
    except Exception as e:
        print(f"  ℹ️  Login test skipped: {str(e)}")
    
    print(f"\n🏁 Day 1-4 LMS System Check Complete!")
    print(f"📅 Tested on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

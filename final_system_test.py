#!/usr/bin/env python
"""
Final System Test - Complete LMS Day 1-4 Verification
Comprehensive test of all implemented features
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

class LMSSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.course_id = None
        self.quiz_id = None
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        
    def test_server_connection(self):
        """Test if Django server is running"""
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/ping/", timeout=5)
            if response.status_code == 200:
                self.log("✅ Server is running", "SUCCESS")
                data = response.json()
                if "version" in data:
                    self.log(f"API Version: {data['version']}")
                return True
            else:
                self.log(f"❌ Server responded with status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Cannot connect to server: {str(e)}", "ERROR")
            return False
    
    def test_user_authentication(self):
        """Test Day 1 - User Authentication System"""
        self.log("=== Testing Day 1 - User Authentication ===")
        
        # Test user signup
        signup_data = {
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "email": f"test_{int(datetime.now().timestamp())}@example.com",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "role": "student"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/signup/", json=signup_data)
            if response.status_code == 201:
                self.log("✅ User signup successful", "SUCCESS")
                user_data = response.json()
                self.user_id = user_data.get("user", {}).get("id")
            else:
                self.log(f"❌ Signup failed: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Signup error: {str(e)}", "ERROR")
            return False
        
        # Test user login
        login_data = {
            "username": signup_data["username"],
            "password": signup_data["password"]
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login/", json=login_data)
            if response.status_code == 200:
                self.log("✅ User login successful", "SUCCESS")
                token_data = response.json()
                self.access_token = token_data.get("access")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            else:
                self.log(f"❌ Login failed: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False
        
        # Test user profile
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/me/")
            if response.status_code == 200:
                self.log("✅ User profile retrieval successful", "SUCCESS")
                profile = response.json()
                self.log(f"User: {profile.get('username')} ({profile.get('role')})")
            else:
                self.log(f"❌ Profile retrieval failed: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Profile error: {str(e)}", "ERROR")
            return False
        
        return True
    
    def test_lms_system(self):
        """Test Day 2 - LMS Core System"""
        self.log("=== Testing Day 2 - LMS Core System ===")
        
        # Test course creation
        course_data = {
            "code": f"TEST{int(datetime.now().timestamp())}",
            "title": "Test Course",
            "description": "A test course for system verification"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/lms/courses/", json=course_data)
            if response.status_code == 201:
                self.log("✅ Course creation successful", "SUCCESS")
                course = response.json()
                self.course_id = course.get("id")
                self.log(f"Course ID: {self.course_id}")
            else:
                self.log(f"❌ Course creation failed: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Course creation error: {str(e)}", "ERROR")
            return False
        
        # Test course listing
        try:
            response = self.session.get(f"{BASE_URL}/api/lms/courses/")
            if response.status_code == 200:
                self.log("✅ Course listing successful", "SUCCESS")
                courses = response.json()
                self.log(f"Found {len(courses.get('results', []))} courses")
            else:
                self.log(f"❌ Course listing failed: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Course listing error: {str(e)}", "ERROR")
            return False
        
        # Test lesson creation
        lesson_data = {
            "title": "Test Lesson",
            "content_url": "https://example.com/lesson1",
            "order": 1,
            "duration": 30
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/lms/courses/{self.course_id}/lessons/", json=lesson_data)
            if response.status_code == 201:
                self.log("✅ Lesson creation successful", "SUCCESS")
            else:
                self.log(f"❌ Lesson creation failed: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Lesson creation error: {str(e)}", "ERROR")
            return False
        
        return True
    
    def test_quiz_system(self):
        """Test Day 3 & 4 - Quiz System"""
        self.log("=== Testing Day 3-4 - Quiz System ===")
        
        if not self.course_id:
            self.log("❌ No course ID available for quiz test", "ERROR")
            return False
        
        # Test quiz creation
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test quiz for system verification",
            "strategy": "fixed",
            "time_limit": 60,
            "attempts_allowed": 3
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/quiz/courses/{self.course_id}/quizzes/", json=quiz_data)
            if response.status_code == 201:
                self.log("✅ Quiz creation successful", "SUCCESS")
                quiz = response.json()
                self.quiz_id = quiz.get("id")
            else:
                self.log(f"❌ Quiz creation failed: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Quiz creation error: {str(e)}", "ERROR")
            return False
        
        # Test question creation
        question_data = {
            "type": "mcq",
            "content": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "answer_key": ["4"],
            "difficulty": 0.5,
            "points": 1,
            "order": 1
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/quiz/quizzes/{self.quiz_id}/questions/", json=question_data)
            if response.status_code == 201:
                self.log("✅ Question creation successful", "SUCCESS")
            else:
                self.log(f"❌ Question creation failed: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Question creation error: {str(e)}", "ERROR")
            return False
        
        # Test adaptive quiz endpoints
        try:
            response = self.session.get(f"{BASE_URL}/api/quiz/adaptive/available-quizzes/")
            if response.status_code == 200:
                self.log("✅ Adaptive quiz listing successful", "SUCCESS")
            else:
                self.log(f"❌ Adaptive quiz listing failed: {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Adaptive quiz listing error: {str(e)}", "ERROR")
        
        return True
    
    def test_api_documentation(self):
        """Test API Documentation"""
        self.log("=== Testing API Documentation ===")
        
        try:
            response = self.session.get(f"{BASE_URL}/api/schema/swagger-ui/")
            if response.status_code == 200:
                self.log("✅ Swagger UI accessible", "SUCCESS")
            else:
                self.log(f"❌ Swagger UI failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Swagger UI error: {str(e)}", "ERROR")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/api/schema/")
            if response.status_code == 200:
                self.log("✅ API Schema accessible", "SUCCESS")
                return True
            else:
                self.log(f"❌ API Schema failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ API Schema error: {str(e)}", "ERROR")
            return False
    
    def run_complete_test(self):
        """Run all tests"""
        self.log("🚀 Starting Complete LMS System Test", "START")
        self.log(f"Testing against: {BASE_URL}")
        
        results = {
            "server_connection": False,
            "user_authentication": False,
            "lms_system": False,
            "quiz_system": False,
            "api_documentation": False
        }
        
        # Run all tests
        results["server_connection"] = self.test_server_connection()
        
        if results["server_connection"]:
            results["user_authentication"] = self.test_user_authentication()
            results["lms_system"] = self.test_lms_system()
            results["quiz_system"] = self.test_quiz_system()
            results["api_documentation"] = self.test_api_documentation()
        
        # Summary
        self.log("=== TEST SUMMARY ===")
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
        
        self.log(f"\nOverall Result: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED - System is ready for production!", "SUCCESS")
            return True
        else:
            self.log(f"⚠️  {total - passed} tests failed - System needs attention", "WARNING")
            return False


if __name__ == "__main__":
    tester = LMSSystemTester()
    success = tester.run_complete_test()
    sys.exit(0 if success else 1)

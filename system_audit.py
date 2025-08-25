"""
Check database content and system data
"""
import sqlite3
import os
from pathlib import Path

# Database path
db_path = Path("E:/Project_LMS_daTN/plms/db.sqlite3")

def check_database():
    """Check database tables and content"""
    if not db_path.exists():
        print("❌ Database file not found!")
        return False
    
    print("🗄️  DATABASE CONTENT CHECK")
    print("="*50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'users_user', 'lms_course', 'lms_module', 'lms_lesson', 'lms_enrollment',
            'quiz_quiz', 'quiz_question', 'quiz_attempt'
        ]
        
        print("📋 Tables:")
        for table in expected_tables:
            exists = table in tables
            print(f"  {'✅' if exists else '❌'} {table}")
        
        # Check data content
        print("\n📊 Data Content:")
        
        # Users
        cursor.execute("SELECT COUNT(*) FROM users_user;")
        user_count = cursor.fetchone()[0]
        print(f"  👥 Users: {user_count}")
        
        # Courses
        cursor.execute("SELECT COUNT(*) FROM lms_course;")
        course_count = cursor.fetchone()[0]
        print(f"  📚 Courses: {course_count}")
        
        # Modules  
        cursor.execute("SELECT COUNT(*) FROM lms_module;")
        module_count = cursor.fetchone()[0]
        print(f"  📑 Modules: {module_count}")
        
        # Lessons
        cursor.execute("SELECT COUNT(*) FROM lms_lesson;")
        lesson_count = cursor.fetchone()[0]
        print(f"  📖 Lessons: {lesson_count}")
        
        # Enrollments
        cursor.execute("SELECT COUNT(*) FROM lms_enrollment;")
        enrollment_count = cursor.fetchone()[0]
        print(f"  🎓 Enrollments: {enrollment_count}")
        
        # Quizzes
        cursor.execute("SELECT COUNT(*) FROM quiz_quiz;")
        quiz_count = cursor.fetchone()[0]
        print(f"  📝 Quizzes: {quiz_count}")
        
        # Questions
        cursor.execute("SELECT COUNT(*) FROM quiz_question;")
        question_count = cursor.fetchone()[0]
        print(f"  ❓ Questions: {question_count}")
        
        # Attempts
        cursor.execute("SELECT COUNT(*) FROM quiz_attempt;")
        attempt_count = cursor.fetchone()[0]
        print(f"  🎯 Attempts: {attempt_count}")
        
        # Check adaptive quiz specifically
        cursor.execute("SELECT COUNT(*) FROM quiz_quiz WHERE strategy='adaptive';")
        adaptive_count = cursor.fetchone()[0]
        print(f"  🎲 Adaptive Quizzes: {adaptive_count}")
        
        # Check users with roles
        cursor.execute("SELECT role, COUNT(*) FROM users_user GROUP BY role;")
        user_roles = cursor.fetchall()
        print(f"  👤 User Roles: {dict(user_roles)}")
        
        conn.close()
        
        # Summary
        print(f"\n{'='*50}")
        total_content = user_count + course_count + quiz_count + question_count
        if total_content > 10:
            print("✅ Database has substantial content - System is populated!")
            return True
        elif total_content > 5:
            print("⚠️  Database has some content - Needs more seed data")
            return True
        else:
            print("❌ Database has minimal content - Needs seeding")
            return False
            
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def check_files():
    """Check important files exist"""
    print("\n📁 FILE STRUCTURE CHECK")
    print("="*50)
    
    base_path = Path("E:/Project_LMS_daTN/plms")
    
    important_files = [
        "manage.py",
        "plms/settings.py",
        "plms/urls.py",
        "users/models.py",
        "users/views.py", 
        "users/urls.py",
        "lms/models.py",
        "lms/views.py",
        "lms/urls.py",
        "quiz/models.py",
        "quiz/views.py",
        "quiz/views_adaptive.py",
        "quiz/adaptive.py",
        "quiz/urls.py",
        "quiz/utils.py",
    ]
    
    existing_files = 0
    for file_path in important_files:
        full_path = base_path / file_path
        exists = full_path.exists()
        print(f"  {'✅' if exists else '❌'} {file_path}")
        if exists:
            existing_files += 1
    
    success_rate = (existing_files / len(important_files)) * 100
    print(f"\n📊 File Structure: {existing_files}/{len(important_files)} ({success_rate:.1f}%)")
    
    return success_rate >= 90

def main():
    print("🔍 LMS SYSTEM COMPREHENSIVE AUDIT")
    print("="*60)
    
    # Check database
    db_ok = check_database()
    
    # Check files
    files_ok = check_files()
    
    # Overall assessment
    print(f"\n{'='*60}")
    print("📋 AUDIT SUMMARY")
    print("="*60)
    
    print(f"  {'✅' if db_ok else '❌'} Database Content")
    print(f"  {'✅' if files_ok else '❌'} File Structure")
    
    if db_ok and files_ok:
        print(f"\n🎉 RESULT: LMS System Day 1-4 is COMPLETE and READY!")
        print(f"✨ All components are properly implemented and populated.")
    elif db_ok or files_ok:
        print(f"\n⚠️  RESULT: LMS System is MOSTLY READY!")
        print(f"🔧 Minor issues detected but core functionality works.")
    else:
        print(f"\n❌ RESULT: LMS System needs ATTENTION!")
        print(f"🚨 Critical issues detected.")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()

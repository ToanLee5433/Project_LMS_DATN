# 🎓 Personal Learning Management System (PLMS) - DATN

## 📋 Tổng Quan
Personal Learning Management System (PLMS) là một hệ thống quản lý học tập cá nhân được phát triển như một phần của Đồ Án Tốt Nghiệp. Hệ thống cung cấp các tính năng quản lý khóa học, bài học, và học viên với kiến trúc REST API hiện đại.

## 🚀 Tính Năng Chính

### ✅ Day 1-2: Core LMS Features (HOÀN THÀNH)
- **👥 User Management**: Hệ thống phân quyền với 3 roles (admin, teacher, student)
- **📚 Course Management**: Quản lý khóa học với CRUD operations
- **📖 Lesson Management**: Quản lý bài học theo thứ tự
- **📝 Enrollment System**: Đăng ký khóa học với role-based access
- **🔐 JWT Authentication**: Bảo mật với JWT tokens
- **🔍 Advanced Filtering**: OrderingFilter + SearchFilter + DjangoFilter
- **✅ Comprehensive Testing**: 7 test cases covering all scenarios
- **📊 Data Validation**: Course code normalization, lesson order validation
- **💬 User-friendly Error Messages**: Vietnamese error messages
- **🎨 Code Quality**: Black formatting, isort, flake8 compliant

### 🔄 Day 3: Quiz System (Sắp tới)
- Quiz creation and management
- Auto-grading system
- Multiple choice questions
- Result tracking

## 🛠️ Tech Stack

### Backend
- **Django 5.2.5**: Web framework
- **Django REST Framework**: API framework
- **django-filter**: Advanced filtering
- **djangorestframework-simplejwt**: JWT authentication
- **drf-spectacular**: API documentation (Swagger)
- **django-cors-headers**: CORS handling

### Database
- **SQLite**: Development database
- **PostgreSQL**: Production ready (configurable)

### Development Tools
- **Black**: Code formatting
- **isort**: Import organization
- **flake8**: Code linting
- **pytest-django**: Testing framework

## 📁 Cấu Trúc Dự Án

```
Project_LMS_daTN/
├── plms/                      # Main Django project
│   ├── plms/                  # Project settings
│   │   ├── settings.py        # Django settings
│   │   ├── urls.py           # Main URL configuration
│   │   └── wsgi.py           # WSGI configuration
│   ├── users/                 # User management app
│   │   ├── models.py         # Custom User model
│   │   ├── serializers.py    # User serializers
│   │   └── views.py          # Authentication views
│   ├── lms/                   # Learning Management System app
│   │   ├── models.py         # Course, Lesson, Enrollment models
│   │   ├── serializers.py    # LMS serializers
│   │   ├── views.py          # LMS API views
│   │   ├── permissions.py    # Custom permissions
│   │   ├── admin.py          # Django admin configuration
│   │   ├── tests.py          # Comprehensive test suite
│   │   └── management/       # Management commands
│   │       └── commands/
│   │           └── seed_lms.py # Database seeding
│   ├── manage.py             # Django management script
│   └── requirements.txt      # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

## 🔧 Cài Đặt và Chạy

### Prerequisites
- Python 3.8+
- pip
- Git

### 1. Clone Repository
```bash
git clone https://github.com/ToanLee5433/Project_LMS_DATN.git
cd Project_LMS_daTN
```

### 2. Tạo Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Cài Đặt Dependencies
```bash
cd plms
pip install -r requirements.txt
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py seed_lms  # Tạo dữ liệu mẫu
```

### 5. Chạy Development Server
```bash
python manage.py runserver
```

API sẽ có sẵn tại: `http://127.0.0.1:8000/api/`

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh

### LMS Endpoints
- `GET /api/lms/courses/` - List courses (with filtering, search, ordering)
- `POST /api/lms/courses/` - Create course (teacher/admin only)
- `GET /api/lms/courses/{id}/` - Course details
- `PUT/PATCH /api/lms/courses/{id}/` - Update course (owner/admin only)
- `DELETE /api/lms/courses/{id}/` - Delete course (owner/admin only)

- `GET /api/lms/lessons/` - List lessons
- `POST /api/lms/lessons/` - Create lesson (course owner/admin only)
- `PUT/PATCH /api/lms/lessons/{id}/` - Update lesson (course owner/admin only)
- `DELETE /api/lms/lessons/{id}/` - Delete lesson (course owner/admin only)

- `GET /api/lms/enrollments/` - List enrollments
- `POST /api/lms/enrollments/` - Enroll in course

### Interactive API Documentation
- Swagger UI: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- ReDoc: `http://127.0.0.1:8000/api/schema/redoc/`

## 🧪 Testing

Chạy test suite:
```bash
python manage.py test lms.tests -v 2
```

### Test Coverage
- **7/7 test cases passing** ✅
- Permission testing (RBAC)
- Data validation testing
- Error handling testing
- Business logic testing

## 📊 Quality Assurance

### Code Quality Tools
```bash
# Code formatting
black .

# Import organization
isort .

# Code linting
flake8 --exclude=.venv,migrations . --max-line-length=88 --extend-ignore=E203,W503,F401
```

### System Checks
```bash
python manage.py check
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control (RBAC)**: 3-tier permission system
- **Input Validation**: Comprehensive data validation
- **CORS Configuration**: Secure cross-origin requests
- **SQL Injection Protection**: Django ORM built-in protection
- **XSS Protection**: Security headers enabled

## 🎯 Roadmap

### ✅ Phase 1 (COMPLETED): Core LMS
- User management system
- Course and lesson management  
- Enrollment system
- Authentication & authorization
- API documentation
- Testing framework

### 🔄 Phase 2 (IN PROGRESS): Quiz System
- Quiz creation interface
- Question management
- Auto-grading engine
- Result analytics
- Performance tracking

### 🚀 Phase 3 (PLANNED): Advanced Features
- Discussion forums
- File upload system
- Progress tracking
- Certificates
- Mobile app support

## 👨‍💻 Development

### Sample Users (from seed_lms command)
```
Admin: admin / admin123
Teacher: teacher1 / teacher1pass
Student: student1 / student1pass
```

### Example API Usage
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "teacher1", "password": "teacher1pass"}'

# Create Course (with JWT token)
curl -X POST http://127.0.0.1:8000/api/lms/courses/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "CS101", "title": "Introduction to Computer Science", "description": "Basic CS concepts"}'
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is part of a graduation thesis (Đồ Án Tốt Nghiệp) and is for educational purposes.

## 📞 Contact

- **Developer**: ToanLee5433
- **Email**: [Your Email]
- **GitHub**: [@ToanLee5433](https://github.com/ToanLee5433)

---

**🎓 Đồ Án Tốt Nghiệp - Personal Learning Management System**  
*Phát triển với ❤️ bằng Django & Django REST Framework*

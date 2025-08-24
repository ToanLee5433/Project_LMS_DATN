# Personal Learning Management System (PLMS)

🎓 **PLMS** là một hệ thống quản lý học tập cá nhân được xây dựng bằng Django REST Framework với JWT Authentication.

## 📋 Tính năng

### ✅ Đã hoàn thành (Ngày 1)
- 🔐 **JWT Authentication** - Đăng nhập/đăng ký với JWT tokens
- 👤 **Custom User Model** - Hỗ trợ role (admin/teacher/student), locale, avatar, ab_group
- 🌐 **REST API** - Các endpoints cơ bản cho authentication
- 📚 **API Documentation** - Swagger/OpenAPI tự động
- 🛡️ **Security** - Password validation, CORS, security headers
- 🧪 **Testing** - Test suite cho tất cả endpoints

### 🔄 Đang phát triển
- 📚 Quản lý khóa học
- 📝 Quản lý bài tập
- 📊 Theo dõi tiến độ học tập
- 💬 Hệ thống thông báo

## 🚀 Cài đặt và Chạy

### 1. Clone repository
```bash
git clone https://github.com/ToanLee5433/Project_LMS_DATN.git
cd Project_LMS_DATN/plms
```

### 2. Tạo virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường
Tạo file `.env`:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver
```

### 5. Database migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo superuser
```bash
python manage.py createsuperuser
```

### 7. Chạy development server
```bash
python manage.py runserver
```

Server sẽ chạy tại: http://127.0.0.1:8000/

## 📚 API Documentation

### Endpoints có sẵn:

#### Authentication
- `GET /api/auth/ping/` - Kiểm tra trạng thái server
- `POST /api/auth/signup/` - Đăng ký tài khoản mới
- `POST /api/auth/token/` - Lấy JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token  
- `GET /api/auth/me/` - Thông tin người dùng hiện tại

### Swagger UI
Truy cập: http://127.0.0.1:8000/api/docs/

### Admin Panel
Truy cập: http://127.0.0.1:8000/admin/

## 🧪 Testing

Chạy test suite:
```bash
python test_django_api.py
```

Kết quả mong đợi:
```
🚀 Testing PLMS API with Django Test Client...

=== TEST PING ===
✅ Ping test passed

=== TEST SIGNUP ===
✅ Signup test passed
✅ Weak password validation works

=== TEST TOKEN ===
✅ Token obtained successfully

=== TEST ME ===
✅ Me endpoint test passed

=== TEST TOKEN REFRESH ===
✅ Token refresh test passed

🎉 All API tests completed!
```

## 🏗️ Cấu trúc dự án

```
plms/
├── .env                    # Environment variables
├── .gitignore             # Git ignore
├── requirements.txt       # Python dependencies
├── manage.py             # Django management
├── db.sqlite3            # SQLite database
├── test_django_api.py    # API test script
├── plms/                 # Main project
│   ├── settings.py       # Django settings
│   └── urls.py          # URL routing
└── users/                # Users app
    ├── models.py         # User model
    ├── serializers.py    # API serializers
    ├── views.py          # API views
    └── urls.py           # App URLs
```

## 💻 Tech Stack

- **Backend:** Django 5.2.5 + Django REST Framework 3.16.1
- **Authentication:** JWT (djangorestframework-simplejwt)
- **API Documentation:** drf-spectacular (Swagger/OpenAPI)
- **Database:** SQLite (development)
- **Security:** CORS headers, password validation
- **Code Quality:** Black, isort, flake8

## 👥 User Model

```python
class User(AbstractUser):
    role = CharField(choices=[("admin","Admin"), ("teacher","Teacher"), ("student","Student")])
    locale = CharField(default="vi")
    avatar = URLField(blank=True, null=True)
    ab_group = CharField(default="CTRL")  # AI/CTRL for A/B testing
    email = EmailField(unique=True)
```

## 🔐 Security Features

- ✅ JWT Authentication với refresh token
- ✅ Password validation (>= 8 chars, không quá đơn giản)
- ✅ Email unique constraint
- ✅ CORS headers cho cross-origin requests
- ✅ Security headers (X-Frame-Options, Content-Type)
- ✅ Environment variables cho sensitive data

## 📈 Roadmap

### Phase 2 (Sắp tới)
- [ ] Course Management
- [ ] Assignment System  
- [ ] Progress Tracking
- [ ] File Upload/Download
- [ ] Real-time Notifications

### Phase 3 (Dài hạn)
- [ ] Video Streaming
- [ ] Quiz System
- [ ] Grading & Analytics
- [ ] Mobile App
- [ ] Advanced Reporting

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 📞 Contact

- **Developer:** ToanLee5433
- **Email:** [Your Email]
- **GitHub:** https://github.com/ToanLee5433

---

⭐ **Star this repo if you find it helpful!** ⭐

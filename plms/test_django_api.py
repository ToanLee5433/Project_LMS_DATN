"""
Simple test script using Django's test client
"""

import os

import django
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plms.settings")
django.setup()

User = get_user_model()


@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
def test_apis():
    client = Client()
    print("🚀 Testing PLMS API with Django Test Client...\n")

    # Test 1: Ping endpoint
    print("=== TEST PING ===")
    response = client.get("/api/auth/ping/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✅ Ping test passed\n")

    # Test 2: Signup endpoint
    print("=== TEST SIGNUP ===")
    signup_data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
    }

    response = client.post(
        "/api/auth/signup/", data=signup_data, content_type="application/json"
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 201:
        expected = {"message": "signed_up", "username": "testuser123"}
        assert response.json() == expected
        print("✅ Signup test passed")
    else:
        print("⚠️ User might already exist, checking for error response...")
        if response.status_code == 400 and "email" in response.json():
            print("✅ Duplicate email validation working")

    # Test weak password
    print("\n--- Test weak password ---")
    weak_data = {
        "username": "testuser456",
        "email": "testuser456@example.com",
        "password": "123",  # Too weak
        "first_name": "Test",
        "last_name": "User",
    }

    response = client.post(
        "/api/auth/signup/", data=weak_data, content_type="application/json"
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Weak password validation works")
    print()

    # Test 3: Token endpoint
    print("=== TEST TOKEN ===")

    # Ensure we have a user to test with
    User.objects.get_or_create(
        username="tokentest",
        defaults={
            "email": "tokentest@example.com",
            "first_name": "Token",
            "last_name": "Test",
        },
    )
    user = User.objects.get(username="tokentest")
    user.set_password("TestPass123!")
    user.save()

    # Get token
    token_data = {"username": "tokentest", "password": "TestPass123!"}

    response = client.post(
        "/api/auth/token/", data=token_data, content_type="application/json"
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        tokens = response.json()
        print("✅ Token obtained successfully")
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]
        print(f"Access token: {access_token[:50]}...")

        # Test 4: Me endpoint with token
        print("\n=== TEST ME ===")
        response = client.get(
            "/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            user_data = response.json()
            print(f"User data: {user_data}")

            # Validate required fields
            required_fields = [
                "id",
                "username",
                "email",
                "first_name",
                "last_name",
                "role",
                "locale",
                "avatar",
                "ab_group",
            ]
            for field in required_fields:
                assert field in user_data, f"Missing field: {field}"

            print("✅ Me endpoint test passed")
        else:
            print(f"❌ Me endpoint failed: {response.json()}")

        # Test 5: Token refresh
        print("\n=== TEST TOKEN REFRESH ===")
        refresh_data = {"refresh": refresh_token}
        response = client.post(
            "/api/auth/token/refresh/",
            data=refresh_data,
            content_type="application/json",
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            response.json()  # Parse response but don't store unused variable
            print("✅ Token refresh test passed")
        else:
            print(f"❌ Token refresh failed: {response.json()}")
    else:
        print(f"❌ Token request failed: {response.json()}")

    print("\n🎉 All API tests completed!")


if __name__ == "__main__":
    test_apis()

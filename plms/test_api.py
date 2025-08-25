#!/usr/bin/env python3
"""
Script test API endpoints của PLMS
"""
import json

import requests

BASE_URL = "http://localhost:8000/api/auth"


def test_ping():
    """Test ping endpoint"""
    print("=== TEST PING ===")
    response = requests.get(f"{BASE_URL}/ping/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✅ Ping test passed\n")


def test_signup():
    """Test signup endpoint"""
    print("=== TEST SIGNUP ===")

    # Test successful signup
    data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
    }

    response = requests.post(f"{BASE_URL}/signup/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 201:
        expected = {"message": "signed_up", "username": "testuser123"}
        assert response.json() == expected
        print("✅ Signup test passed")
    else:
        print("⚠️ User might already exist")

    # Test duplicate email
    print("\n--- Test duplicate email ---")
    response2 = requests.post(f"{BASE_URL}/signup/", json=data)
    print(f"Status: {response2.status_code}")
    if response2.status_code == 400:
        print(f"Response: {response2.json()}")
        print("✅ Duplicate email validation works")

    # Test weak password
    print("\n--- Test weak password ---")
    weak_data = {
        "username": "testuser456",
        "email": "testuser456@example.com",
        "password": "123",  # Too weak
        "first_name": "Test",
        "last_name": "User",
    }

    response3 = requests.post(f"{BASE_URL}/signup/", json=weak_data)
    print(f"Status: {response3.status_code}")
    if response3.status_code == 400:
        print(f"Response: {response3.json()}")
        print("✅ Weak password validation works")
    print()


def test_token():
    """Test token endpoint"""
    print("=== TEST TOKEN ===")

    # First ensure we have a user
    signup_data = {
        "username": "tokentest",
        "email": "tokentest@example.com",
        "password": "TestPass123!",
        "first_name": "Token",
        "last_name": "Test",
    }
    requests.post(f"{BASE_URL}/signup/", json=signup_data)

    # Get token
    token_data = {"username": "tokentest", "password": "TestPass123!"}

    response = requests.post(f"{BASE_URL}/token/", json=token_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        token_response = response.json()
        print("✅ Token obtained successfully")
        print(f"Access token: {token_response['access'][:50]}...")
        print(f"Refresh token: {token_response['refresh'][:50]}...")
        return token_response
    else:
        print(f"❌ Token request failed: {response.json()}")
        return None


def test_me(access_token):
    """Test me endpoint with JWT token"""
    print("=== TEST ME ===")

    if not access_token:
        print("❌ No access token available")
        return

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/me/", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"User data: {json.dumps(user_data, indent=2)}")

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


def test_token_refresh(refresh_token):
    """Test token refresh endpoint"""
    print("=== TEST TOKEN REFRESH ===")

    if not refresh_token:
        print("❌ No refresh token available")
        return

    refresh_data = {"refresh": refresh_token}
    response = requests.post(f"{BASE_URL}/token/refresh/", json=refresh_data)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        new_token = response.json()
        print(f"New access token: {new_token['access'][:50]}...")
        print("✅ Token refresh test passed")
        return new_token["access"]
    else:
        print(f"❌ Token refresh failed: {response.json()}")
        return None


if __name__ == "__main__":
    try:
        print("🚀 Testing PLMS API Endpoints...\n")

        test_ping()
        test_signup()

        tokens = test_token()
        if tokens:
            test_me(tokens["access"])
            test_token_refresh(tokens["refresh"])

        print("🎉 All API tests completed!")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Cannot connect to server. Make sure Django server is running "
            "at http://localhost:8000"
        )
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()

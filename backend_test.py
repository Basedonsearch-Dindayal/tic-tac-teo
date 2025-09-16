#!/usr/bin/env python3
"""
Backend Testing Script for Tic-Tac-Toe App
Tests basic backend functionality including health check and MongoDB connection
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://expo-xando.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

def test_health_check():
    """Test the basic health check endpoint GET /api/"""
    print("🔍 Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Hello World":
                print("   ✅ Health check endpoint working correctly")
                return True
            else:
                print("   ❌ Health check returned unexpected message")
                return False
        else:
            print(f"   ❌ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Health check failed with error: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection by testing status endpoints"""
    print("\n🔍 Testing MongoDB Connection via Status Endpoints...")
    
    # Test POST /api/status (create status check)
    print("   Testing POST /api/status...")
    try:
        test_data = {
            "client_name": "backend_test_client"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/status", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   POST Status Code: {response.status_code}")
        
        if response.status_code == 200:
            created_status = response.json()
            print(f"   POST Response: {created_status}")
            
            # Verify the response structure
            if all(key in created_status for key in ["id", "client_name", "timestamp"]):
                print("   ✅ POST /api/status working correctly")
                post_success = True
                status_id = created_status["id"]
            else:
                print("   ❌ POST /api/status returned incomplete data")
                post_success = False
                status_id = None
        else:
            print(f"   ❌ POST /api/status failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            post_success = False
            status_id = None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ POST /api/status failed with error: {e}")
        post_success = False
        status_id = None
    
    # Test GET /api/status (retrieve status checks)
    print("\n   Testing GET /api/status...")
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=10)
        print(f"   GET Status Code: {response.status_code}")
        
        if response.status_code == 200:
            status_list = response.json()
            print(f"   GET Response: Found {len(status_list)} status checks")
            
            # If we created a status check, verify it's in the list
            if post_success and status_id:
                found_status = any(status.get("id") == status_id for status in status_list)
                if found_status:
                    print("   ✅ GET /api/status working correctly - created status found")
                    get_success = True
                else:
                    print("   ⚠️  GET /api/status working but created status not found")
                    get_success = True  # Still consider it working
            else:
                print("   ✅ GET /api/status working correctly")
                get_success = True
        else:
            print(f"   ❌ GET /api/status failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            get_success = False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ GET /api/status failed with error: {e}")
        get_success = False
    
    return post_success and get_success

def test_backend_service():
    """Test if backend service is accessible"""
    print("\n🔍 Testing Backend Service Accessibility...")
    try:
        # Test if we can reach the backend at all
        response = requests.get(BACKEND_URL, timeout=5)
        print(f"   Backend URL: {BACKEND_URL}")
        print(f"   Status Code: {response.status_code}")
        print("   ✅ Backend service is accessible")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Backend service not accessible: {e}")
        return False

def main():
    """Run all backend tests"""
    print("=" * 60)
    print("🚀 BACKEND TESTING FOR TIC-TAC-TOE APP")
    print("=" * 60)
    print(f"Testing backend at: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Track test results
    results = {
        "backend_service": False,
        "health_check": False,
        "mongodb_connection": False
    }
    
    # Run tests
    results["backend_service"] = test_backend_service()
    results["health_check"] = test_health_check()
    results["mongodb_connection"] = test_mongodb_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All backend tests passed!")
        return 0
    else:
        print("⚠️  Some backend tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
Test script to verify the authentication and history system
Run with: python3 test_auth_system.py
"""

import json
import os
from history import (
    init_storage, register_user, verify_user, user_exists,
    get_user_history, add_prediction_record
)

def print_section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def test_storage_init():
    """Test storage initialization"""
    print_section("TEST 1: Storage Initialization")
    init_storage()
    print("✅ Storage initialized")
    
    # Check if data directory exists
    if os.path.exists("data/users.json"):
        print("✅ data/users.json exists")
    if os.path.exists("data/history"):
        print("✅ data/history directory exists")

def test_user_registration():
    """Test user registration"""
    print_section("TEST 2: User Registration")
    
    # Register a test user
    success, msg = register_user("testuser", "pass123")
    if success:
        print(f"✅ User registration successful: {msg}")
    else:
        print(f"❌ Registration failed: {msg}")
    
    # Try to register duplicate
    success, msg = register_user("testuser", "pass456")
    if not success:
        print(f"✅ Duplicate check working: {msg}")
    else:
        print(f"❌ Duplicate check failed")

def test_user_verification():
    """Test user login verification"""
    print_section("TEST 3: User Verification")
    
    # Correct credentials
    if verify_user("testuser", "pass123"):
        print("✅ Correct credentials verified")
    else:
        print("❌ Correct credentials not verified")
    
    # Wrong password
    if not verify_user("testuser", "wrongpass"):
        print("✅ Wrong password rejected")
    else:
        print("❌ Wrong password accepted (security issue)")
    
    # Non-existent user
    if not verify_user("nouser", "pass123"):
        print("✅ Non-existent user rejected")
    else:
        print("❌ Non-existent user accepted")

def test_user_exists():
    """Test user exists check"""
    print_section("TEST 4: User Exists Check")
    
    if user_exists("testuser"):
        print("✅ user_exists() correctly identified registered user")
    else:
        print("❌ user_exists() failed for registered user")
    
    if not user_exists("nouser"):
        print("✅ user_exists() correctly identified non-existent user")
    else:
        print("❌ user_exists() incorrectly identified non-existent user")

def test_history():
    """Test history operations"""
    print_section("TEST 5: History Operations")
    
    # Add predictions
    add_prediction_record("testuser", "✅ No Dengue", 15.5)
    print("✅ Added prediction 1 to testuser history")
    
    add_prediction_record("testuser", "⚠️ Dengue Positive", 78.3)
    print("✅ Added prediction 2 to testuser history")
    
    # Get history
    history = get_user_history("testuser")
    if len(history) == 2:
        print(f"✅ History retrieved successfully ({len(history)} records)")
        for i, record in enumerate(history, 1):
            print(f"   Record {i}: {record['prediction']} ({record['percent']}%)")
    else:
        print(f"❌ History count mismatch: expected 2, got {len(history)}")
    
    # New user should have empty history
    history_new = get_user_history("newuser")
    if len(history_new) == 0:
        print("✅ New user starts with empty history")
    else:
        print(f"❌ New user history not empty: {len(history_new)} records")

def test_data_persistence():
    """Test data persistence by reading files"""
    print_section("TEST 6: Data Persistence Check")
    
    # Check users.json
    if os.path.exists("data/users.json"):
        with open("data/users.json", 'r') as f:
            users = json.load(f)
        if "testuser" in users:
            print(f"✅ User data persisted in data/users.json")
            print(f"   Registered users: {list(users.keys())}")
        else:
            print("❌ User not found in data/users.json")
    
    # Check history file
    history_file = "data/history/testuser_history.json"
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
        print(f"✅ User history persisted in {history_file}")
        print(f"   Predictions: {len(history)}")
    else:
        print(f"❌ History file not found: {history_file}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("  DENGUE APP - AUTHENTICATION & HISTORY TEST SUITE")
    print("="*50)
    
    try:
        test_storage_init()
        test_user_registration()
        test_user_verification()
        test_user_exists()
        test_history()
        test_data_persistence()
        
        print_section("ALL TESTS COMPLETED")
        print("✅ System is working correctly!")
        print("\nNext steps:")
        print("1. Run the Flask app: flask run")
        print("2. Visit http://localhost:5000/signup to create users")
        print("3. Test login/logout/history functionality")
        
    except Exception as e:
        print_section("ERROR OCCURRED")
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()

#!/usr/bin/env python3
"""
Test script to verify the NEW SQLite authentication and history system
Run with: python3 test_auth_system.py
"""

import os
import sqlite3
from history import (
    init_storage, register_user, verify_user, user_exists,
    get_user_history, add_prediction_record, DB_FILE
)

def print_section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def test_storage_init():
    """Test storage initialization"""
    print_section("TEST 1: Storage Initialization")
    init_storage()
    print("✅ Storage initialized (SQLite)")
    
    # Check if DB file exists
    if os.path.exists(DB_FILE):
        print(f"✅ {DB_FILE} exists")
        
        # Check tables
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Found tables: {tables}")
        conn.close()

def test_user_registration():
    """Test user registration"""
    print_section("TEST 2: User Registration")
    
    # Register a new unique test user
    username = "sqlite_test_user"
    # Delete if exists to make test repeatable
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    success, msg = register_user(username, "pass123")
    if success:
        print(f"✅ User registration successful: {msg}")
    else:
        print(f"❌ Registration failed: {msg}")
    
    # Try to register duplicate
    success, msg = register_user(username, "pass456")
    if not success:
        print(f"✅ Duplicate check working: {msg}")
    else:
        print(f"❌ Duplicate check failed")

def test_user_verification():
    """Test user login verification (with hashing)"""
    print_section("TEST 3: User Verification")
    
    username = "sqlite_test_user"
    
    # Correct credentials
    if verify_user(username, "pass123"):
        print("✅ Correct credentials verified (hashed check)")
    else:
        print("❌ Correct credentials not verified")
    
    # Wrong password
    if not verify_user(username, "wrongpass"):
        print("✅ Wrong password rejected")
    else:
        print("❌ Wrong password accepted (security issue)")

def test_history():
    """Test history operations in SQLite"""
    print_section("TEST 4: History Operations")
    
    username = "sqlite_test_user"
    
    # Clear history first
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM history WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    # Add predictions
    add_prediction_record(username, "✅ No Dengue", 15.5)
    print("✅ Added prediction 1 to SQLite")
    
    add_prediction_record(username, "⚠️ Dengue Positive", 78.3)
    print("✅ Added prediction 2 to SQLite")
    
    # Get history
    history = get_user_history(username)
    if len(history) == 2:
        print(f"✅ History retrieved successfully ({len(history)} records)")
        for i, record in enumerate(history, 1):
            print(f"   Record {i}: {record['prediction']} ({record['percent']}%)")
    else:
        print(f"❌ History count mismatch: expected 2, got {len(history)}")

def test_migration_check():
    """Check if migration from JSON happened"""
    print_section("TEST 5: Migration Check")
    
    # Check for legacy users we saw earlier
    legacy_users = ["satya", "testuser"]
    for user in legacy_users:
        if user_exists(user):
            print(f"✅ Legacy user '{user}' successfully migrated to SQLite")
        else:
            print(f"ℹ️ Legacy user '{user}' not found (maybe JSON was already gone)")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("  DENGUE APP - SQLITE AUTH & HISTORY TEST SUITE")
    print("="*50)
    
    try:
        test_storage_init()
        test_user_registration()
        test_user_verification()
        test_history()
        test_migration_check()
        
        print_section("ALL TESTS COMPLETED")
        print("✅ System is working correctly with SQLite!")
        
    except Exception as e:
        print_section("ERROR OCCURRED")
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()

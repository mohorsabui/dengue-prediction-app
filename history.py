import json
import os
from datetime import datetime

# Data files
USERS_FILE = "data/users.json"
HISTORY_DIR = "data/history"

# Initialize data directory
def init_storage():
    """Initialize storage directories and files"""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    # Create users.json if it doesn't exist
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)

# USER MANAGEMENT
def get_all_users():
    """Load all users from storage"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def user_exists(username):
    """Check if user exists"""
    users = get_all_users()
    return username in users

def register_user(username, password):
    """Register a new user"""
    users = get_all_users()
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        "password": password,
        "created_at": datetime.now().isoformat()
    }
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    
    # Create user history file
    user_history_file = os.path.join(HISTORY_DIR, f"{username}_history.json")
    with open(user_history_file, 'w') as f:
        json.dump([], f)
    
    return True, "User registered successfully"

def verify_user(username, password):
    """Verify user credentials"""
    users = get_all_users()
    if username not in users:
        return False
    
    return users[username]["password"] == password

# HISTORY MANAGEMENT
def get_user_history(username):
    """Get all history records for a user"""
    history_file = os.path.join(HISTORY_DIR, f"{username}_history.json")
    
    if not os.path.exists(history_file):
        return []
    
    try:
        with open(history_file, 'r') as f:
            return json.load(f)
    except:
        return []

def add_prediction_record(username, prediction_text, probability):
    """Add a prediction record to user history"""
    history = get_user_history(username)
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "time": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "prediction": prediction_text,
        "percent": probability  # Using "percent" to match chart.js expectations
    }
    
    history.append(record)
    
    # Save updated history
    history_file = os.path.join(HISTORY_DIR, f"{username}_history.json")
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    return record

def clear_user_history(username):
    """Clear all history for a user"""
    history_file = os.path.join(HISTORY_DIR, f"{username}_history.json")
    
    with open(history_file, 'w') as f:
        json.dump([], f)
    
    return True

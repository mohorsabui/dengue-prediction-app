import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Database file
DB_FILE = "data/dengue_app.db"

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_storage():
    """Initialize storage directories and SQLite tables"""
    os.makedirs("data", exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    # Create history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        time TEXT NOT NULL,
        date TEXT NOT NULL,
        prediction TEXT NOT NULL,
        percent REAL NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )
    ''')
    
    conn.commit()
    
    # MIGRATION: If old JSON files exist, import them
    migrate_from_json(conn)
    
    conn.close()

def migrate_from_json(conn):
    """Migrate data from legacy JSON files to SQLite for permanent storage"""
    USERS_FILE = "data/users.json"
    HISTORY_DIR = "data/history"
    
    # 1. Migrate Users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                users_data = json.load(f)
            
            cursor = conn.cursor()
            migrated_count = 0
            for username, info in users_data.items():
                # Check if user already in DB
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if not cursor.fetchone():
                    # If password is already a hash, keep it, otherwise hash it
                    pwd = info['password']
                    if not pwd.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
                        pwd = generate_password_hash(pwd)
                    
                    cursor.execute(
                        "INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
                        (username, pwd, info.get('created_at', datetime.now().isoformat()))
                    )
                    migrated_count += 1
            conn.commit()
            if migrated_count > 0:
                print(f"📦 Migrated {migrated_count} users from JSON to SQLite")
            
            # 2. Migrate History
            if os.path.exists(HISTORY_DIR):
                history_count = 0
                for filename in os.listdir(HISTORY_DIR):
                    if filename.endswith("_history.json"):
                        username = filename.replace("_history.json", "")
                        history_path = os.path.join(HISTORY_DIR, filename)
                        
                        try:
                            with open(history_path, 'r') as f:
                                records = json.load(f)
                            
                            for r in records:
                                # Avoid duplicates by checking timestamp
                                cursor.execute(
                                    "SELECT id FROM history WHERE username = ? AND timestamp = ?",
                                    (username, r['timestamp'])
                                )
                                if not cursor.fetchone():
                                    cursor.execute(
                                        "INSERT INTO history (username, timestamp, time, date, prediction, percent) VALUES (?, ?, ?, ?, ?, ?)",
                                        (username, r['timestamp'], r['time'], r.get('date', datetime.now().strftime("%Y-%m-%d")), r['prediction'], r['percent'])
                                    )
                                    history_count += 1
                        except Exception as e:
                            print(f"⚠️ Error migrating history for {username}: {e}")
                
                conn.commit()
                if history_count > 0:
                    print(f"📦 Migrated {history_count} history records from JSON to SQLite")
            
            # Note: We keep the old files as backup for now, but they won't be used
            
        except Exception as e:
            print(f"⚠️ Migration error: {e}")

def get_all_users():
    """Load all usernames from storage"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = [row['username'] for row in cursor.fetchall()]
    conn.close()
    return users

def user_exists(username):
    """Check if user exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def register_user(username, password):
    """Register a new user with hashed password for security"""
    if not username or not password:
        return False, "Username and password are required"
        
    if user_exists(username):
        return False, "Username already exists"
    
    hashed_password = generate_password_hash(password)
    created_at = datetime.now().isoformat()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
            (username, hashed_password, created_at)
        )
        conn.commit()
        conn.close()
        return True, "User registered successfully"
    except Exception as e:
        return False, f"Database error: {e}"

def verify_user(username, password):
    """Verify user credentials using hash check"""
    if not username or not password:
        return False
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False
    
    stored_pwd = row['password']
    # Check if it's a hash or plain text (migration fallback)
    if stored_pwd.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
        return check_password_hash(stored_pwd, password)
    else:
        # Fallback for unhashed migration if needed (though migrate_from_json hashes them)
        return stored_pwd == password

def get_user_history(username):
    """Get all history records for a user from SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, time, date, prediction, percent FROM history WHERE username = ? ORDER BY timestamp DESC",
        (username,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def add_prediction_record(username, prediction_text, probability):
    """Add a prediction record to user history in SQLite"""
    now = datetime.now()
    record = {
        "timestamp": now.isoformat(),
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "prediction": prediction_text,
        "percent": float(probability)
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (username, timestamp, time, date, prediction, percent) VALUES (?, ?, ?, ?, ?, ?)",
            (username, record['timestamp'], record['time'], record['date'], record['prediction'], record['percent'])
        )
        conn.commit()
        conn.close()
        return record
    except Exception as e:
        print(f"⚠️ Error saving prediction: {e}")
        return None

def clear_user_history(username):
    """Clear all history for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Error clearing history: {e}")
        return False

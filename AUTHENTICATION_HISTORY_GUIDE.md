# Dengue Prediction App - Permanent Storage System (SQLite)

## Overview

The authentication and history system has been upgraded from JSON files to **SQLite**, providing permanent, reliable, and secure storage that survives app restarts and prevents data corruption.

## Key Upgrades

### 1. **SQLite Database Engine**
- **File**: `data/dengue_app.db`
- Replaces legacy `data/users.json` and `data/history/*.json` files.
- Provides ACID compliance (Atomicity, Consistency, Isolation, Durability) to ensure data is never lost or corrupted during crashes or restarts.

### 2. **Password Hashing (Security)**
- Passwords are no longer stored in plain text.
- Uses `werkzeug.security` (PBKDF2 with salt) to securely hash passwords.
- Even if the database file is accessed, user passwords remain protected.

### 3. **Automatic Migration**
- On the first run, the system automatically detects legacy JSON files.
- It imports all users and their prediction history into the new SQLite database.
- It automatically hashes legacy plain-text passwords during the import.

### 4. **Improved History Management**
- All history is stored in a single `history` table with a foreign key relationship to users.
- Faster queries and better data integrity.

## Database Schema

### Users Table
| Column | Type | Description |
| --- | --- | --- |
| id | INTEGER | Primary Key |
| username | TEXT | Unique Username |
| password | TEXT | Hashed Password |
| created_at | TEXT | ISO Timestamp |

### History Table
| Column | Type | Description |
| --- | --- | --- |
| id | INTEGER | Primary Key |
| username | TEXT | Foreign Key to Users |
| timestamp | TEXT | ISO Timestamp |
| time | TEXT | HH:MM:SS |
| date | TEXT | YYYY-MM-DD |
| prediction | TEXT | Result Text |
| percent | REAL | Probability Percentage |

## How to Verify Persistence

1. **Signup**: Create an account on the `/signup` page.
2. **Login**: Log in with your credentials.
3. **Restart**: Stop the Flask server (`Ctrl+C`) and start it again (`flask run`).
4. **Login Again**: Use the same credentials. You will find that:
   - Your account still exists.
   - Your prediction history is fully preserved.

## Technical Details

The `history.py` module now handles all database interactions using the `sqlite3` library. The API remains compatible with `app.py`, so no changes were required in the main application logic.

### New Functions in `history.py`
- `get_db_connection()`: Manages SQLite connections.
- `migrate_from_json()`: Handles legacy data import.
- `init_storage()`: Creates tables and triggers migration.

## Troubleshooting

If you encounter "Invalid credentials" after migration:
1. Ensure you are using the correct casing for your username (usernames are currently case-sensitive).
2. Check `data/dengue_app.db` using a SQLite browser if you need to verify the data manually.

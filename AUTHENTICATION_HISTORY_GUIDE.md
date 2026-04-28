# Dengue Prediction App - Updated Authentication & History System

## Changes Made

### 1. **Persistent User Storage** 
- Created `history.py` module with persistent storage functions
- User credentials now saved to `data/users.json` (survives app restarts)
- Each user gets their own history file: `data/history/{username}_history.json`

### 2. **Fixed Login Logic**
- Updated `/login` route to verify credentials from persistent storage
- Fixed issue where users couldn't login on subsequent sessions
- Added proper validation and error messages

### 3. **Fixed Signup Logic**
- Updated `/signup` route to save user data to `data/users.json`
- Creates individual history file for each new user
- Added duplicate username check
- Validates empty fields

### 4. **History Tracking Per User**
- Every prediction is now saved with:
  - Timestamp (ISO format + readable time)
  - Date
  - Prediction result (Dengue Positive/Negative)
  - Probability percentage
- History persists across sessions and app restarts
- Each user only sees their own history

## How It Works

### Directory Structure
```
data/
├── users.json              # All registered users and passwords
└── history/
    ├── user1_history.json
    ├── user2_history.json
    └── ...
```

### User Flow
1. **Signup**: User registers → Data saved to `data/users.json` → Empty history file created
2. **Login**: Credentials verified from `data/users.json` → Session created
3. **Dashboard**: User history loaded from `data/history/{username}_history.json`
4. **Predict**: Prediction made → Record saved to user's history file
5. **History**: User can see all their past predictions

## Testing

### Manual Testing Steps

1. **Test Signup**
   - Go to `/signup`
   - Create new user (e.g., "testuser" / "password123")
   - Should be redirected to login
   - Check `data/users.json` - should contain the new user

2. **Test Login**
   - Use the credentials from signup
   - Should access dashboard
   - Check that session is active

3. **Test Persistent Login**
   - Make a prediction
   - Logout
   - Login again with same credentials
   - Dashboard should load with previous history

4. **Test History**
   - Make multiple predictions
   - Each should appear in history
   - Check `data/history/{username}_history.json` file
   - Logout and login - history should persist

### File Checking
```bash
# Check users registered
cat data/users.json

# Check specific user's history
cat data/history/testuser_history.json
```

## API Changes

### New Functions in `history.py`
- `init_storage()` - Initialize storage on app startup
- `register_user(username, password)` - Save new user
- `verify_user(username, password)` - Check credentials
- `get_user_history(username)` - Fetch user's history
- `add_prediction_record(username, prediction_text, probability)` - Save prediction
- `clear_user_history(username)` - Clear user history (utility)

## Security Notes
⚠️ **Important**: 
- Passwords are currently stored in plain text (NOT recommended for production)
- For production, implement proper password hashing (e.g., bcrypt)
- Use environment variables for sensitive data
- Consider using a database instead of JSON files for scalability

## Next Steps (Recommendations)
1. Add password hashing using `werkzeug.security` or `bcrypt`
2. Migrate to a database (SQLite, PostgreSQL)
3. Add user email verification
4. Add "Clear History" button in dashboard
5. Add export history as CSV feature
6. Add time-based filtering for history

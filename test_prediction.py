import requests
import json

# Test prediction with low symptoms
data_low = {
    'days': 1,
    'temp': 37.0,
    'wbc': 7000,
    'headache': 0,
    'eye_pain': 0,
    'joint_pain': 0,
    'metallic': 0,
    'appetite': 0,
    'abdominal': 0,
    'nausea': 0,
    'diarrhoea': 0,
    'hemoglobin': 14.0,
    'hematocrit': 40.0,
    'platelet': 250000
}

# Test prediction with high symptoms
data_high = {
    'days': 5,
    'temp': 40.0,
    'wbc': 4000,
    'headache': 1,
    'eye_pain': 1,
    'joint_pain': 1,
    'metallic': 1,
    'appetite': 1,
    'abdominal': 1,
    'nausea': 1,
    'diarrhoea': 1,
    'hemoglobin': 10.0,
    'hematocrit': 30.0,
    'platelet': 50000
}

# Start session
session = requests.Session()

# Signup first
signup_data = {'username': 'test', 'password': 'test'}
response = session.post('http://127.0.0.1:5000/signup', data=signup_data)
print(f"Signup status: {response.status_code}")

# Login
login_data = {'username': 'test', 'password': 'test'}
response = session.post('http://127.0.0.1:5000/login', data=login_data)
print(f"Login status: {response.status_code}")

# Test low symptoms
response = session.post('http://127.0.0.1:5000/predict', data=data_low)
print(f"Low symptoms prediction: {response.text}")

# Test high symptoms
response = session.post('http://127.0.0.1:5000/predict', data=data_high)
print(f"High symptoms prediction: {response.text}")
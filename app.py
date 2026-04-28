from flask import Flask, render_template, request, redirect, session
import pickle
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai
import csv
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from history import init_storage, get_all_users, user_exists, register_user, verify_user, get_user_history, add_prediction_record

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "secret123"

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print(f"Gemini API configured successfully")
else:
    print("Warning: GEMINI_API_KEY not found in .env file")

# Model training function
def train_model():
    data = []
    with open('dengue.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            data.append([float(x) for x in row])
    
    X = [row[:-1] for row in data]
    y = [row[-1] for row in data]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    model = LogisticRegression(random_state=42)
    model.fit(X_train_scaled, y_train)
    
    pickle.dump((model, scaler), open("linear_model.pkl", "wb"))
    print("Model retrained and saved as linear_model.pkl")
    return model, scaler

# Preprocess input function
def preprocess_input(features):
    # Ensure features are floats and handle any cleaning
    return [float(f) for f in features]

# Load or retrain model
model_path = 'linear_model.pkl'
csv_path = 'dengue.csv'
if not os.path.exists(model_path) or os.path.getmtime(csv_path) > os.path.getmtime(model_path):
    dengue_model, scaler = train_model()
    model_mtime = os.path.getmtime(model_path)
else:
    dengue_model, scaler = pickle.load(open(model_path, "rb"))
    model_mtime = os.path.getmtime(model_path)
    print("Loaded existing model from linear_model.pkl")

# Initialize Gemini model with system instruction for better consistency
model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction="""You are a professional dengue medical assistant. 
Strict Rules:
1. Provide a helpful and safe response in 1-3 lines.
2. ALWAYS end your response with a full stop. NEVER stop mid-sentence.
3. Ensure every sentence is complete and logical.
4. Advice: Hydration, paracetamol, rest. NO aspirin or NSAIDs.
5. Emergencies: vomiting, bleeding, or severe pain require immediate medical attention."""
)

# Initialize persistent storage
init_storage()
print("✅ Storage initialized successfully")

# ---------------- HOME ---------------- #
@app.route("/")
def home():
    return redirect("/login")

# ---------------- LOGIN ---------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if verify_user(u, p):
            session["user"] = u
            print(f"✅ User '{u}' logged in successfully")
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# ---------------- SIGNUP ---------------- #
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if user_exists(u):
            return render_template("signup.html", error="Username already exists")
        
        if not u or not p:
            return render_template("signup.html", error="Username and password are required")
        
        success, message = register_user(u, p)
        if success:
            print(f"✅ User '{u}' registered successfully")
            return redirect("/login")
        else:
            return render_template("signup.html", error=message)

    return render_template("signup.html")

# ---------------- LOGOUT ---------------- #
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- DASHBOARD ---------------- #
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    user_history = get_user_history(user)
    
    return render_template(
        "index.html",
        history=user_history
    )

# ---------------- PREDICT ---------------- #
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    # Check if dataset updated, retrain if needed
    global dengue_model, scaler, model_mtime
    if os.path.getmtime(csv_path) > model_mtime:
        dengue_model, scaler = train_model()
        model_mtime = os.path.getmtime(model_path)

    features = [
        request.form["days"],
        request.form["temp"],
        request.form["wbc"],
        request.form["headache"],
        request.form["eye_pain"],
        request.form["joint_pain"],
        request.form["metallic"],
        request.form["appetite"],
        request.form["abdominal"],
        request.form["nausea"],
        request.form["diarrhoea"],
        request.form["hemoglobin"],
        request.form["hematocrit"],
        request.form["platelet"]
    ]

    # Preprocess features
    features = preprocess_input(features)

    # Scale features
    features_scaled = scaler.transform([features])

    pred = dengue_model.predict(features_scaled)[0]
    prob = dengue_model.predict_proba(features_scaled)[0][1]

    result = "⚠️ Dengue Positive" if pred == 1 else "✅ No Dengue"
    percent = round(prob * 100, 2)
    percent = max(0, min(100, percent))  # Clamp between 0-100

    # Save prediction to user history
    add_prediction_record(user, result, percent)
    
    # Get updated history
    user_history = get_user_history(user)

    return {
        "prediction_text": result,
        "probability": percent,
        "history": user_history
    }

# Local fallback advice for basic dengue questions
DENGUE_ADVICE = [
    "Stay hydrated (water, ORS, juices) and get plenty of rest.",
    "Use paracetamol for fever and pain. DO NOT take aspirin, ibuprofen, or other NSAIDs as they increase bleeding risk.",
    "Monitor for emergency signs: severe abdominal pain, persistent vomiting, bleeding gums, or extreme weakness.",
    "Dengue is a viral infection; there is no specific medicine. Support your body with fluids and rest.",
    "If you have a high fever and joint pain, please see a doctor for a blood test."
]

import random

# ---------------- CHATBOT ---------------- #
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json["message"]
    except:
        return {"reply": "Invalid request format. Please send a valid JSON message."}
    
    try:
        # Use Chat Session for better context and completeness
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(
            user_message,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1024, # High token limit to allow complete thoughts
                temperature=0.7 # Slightly higher for more natural flow
            )
        )
        
        reply = response.text.strip()
        
        # Security check: if the model still gives an unfinished sentence (rare with 1024 tokens)
        if reply and not reply.endswith(('.', '!', '?')):
            reply += " Please consult a doctor for further details."
            
        return {"reply": reply}
    
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        fallback = " ".join(random.sample(DENGUE_ADVICE, 2))
        return {
            "reply": f"Note: I'm currently in offline mode. {fallback}"
        }

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
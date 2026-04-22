from flask import Flask, render_template, request, redirect, session
import pickle
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai

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

# Load dengue prediction model
dengue_model = pickle.load(open("dengue_model.pkl", "rb"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

# Storage
users = {}
history = {}

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

        if u in users and users[u] == p:
            session["user"] = u

            # 🔥 FIX: ensure history exists
            if u not in history:
                history[u] = []

            return redirect("/dashboard")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# ---------------- SIGNUP ---------------- #
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        users[u] = p
        history[u] = []   # create history at signup

        return redirect("/login")

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

    return render_template(
        "index.html",
        history=history.get(session["user"], [])
    )

# ---------------- PREDICT ---------------- #
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    features = [
        float(request.form["days"]),
        float(request.form["temp"]),
        float(request.form["wbc"]),
        float(request.form["headache"]),
        float(request.form["eye_pain"]),
        float(request.form["joint_pain"]),
        float(request.form["metallic"]),
        float(request.form["appetite"]),
        float(request.form["abdominal"]),
        float(request.form["nausea"]),
        float(request.form["diarrhoea"]),
        float(request.form["hemoglobin"]),
        float(request.form["hematocrit"]),
        float(request.form["platelet"])
    ]

    pred = dengue_model.predict([features])[0]
    prob = dengue_model.predict_proba([features])[0][1]

    result = "⚠️ Dengue Positive" if pred == 1 else "✅ No Dengue"
    percent = round(prob * 100, 2)

    record = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "percent": percent
    }

    # 🔥 FINAL FIX (no KeyError ever)
    history.setdefault(user, []).append(record)

    return render_template(
        "index.html",
        prediction_text=result,
        probability=percent,
        history=history[user]
    )

# ---------------- CHATBOT ---------------- #
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json["message"]
    except:
        return {"reply": "Invalid request format. Please send a valid JSON message."}
    
    # Short, efficient system prompt
    system_prompt = """You are a dengue medical assistant. Provide safe, concise advice (2-3 sentences max).
Emphasize: hydration, paracetamol for fever, rest, and avoid aspirin/NSAIDs.
Warn to see a doctor immediately for: vomiting, bleeding, severe pain, or weakness."""
    
    # Retry logic for quota errors
    import time
    max_retries = 2
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Send message to Gemini API
            full_message = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
            response = model.generate_content(
                full_message,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=0.5
                )
            )
            
            reply = response.text.strip()
            print(f"Gemini API Success (attempt {attempt + 1}): {len(reply)} chars")
            return {"reply": reply}
        
        except Exception as e:
            error_msg = str(e)
            print(f"Gemini API Error (attempt {attempt + 1}): {error_msg}")
            
            # If 429, retry after delay
            if "429" in error_msg or "quota" in error_msg.lower():
                if attempt < max_retries - 1:
                    print(f"Quota exceeded. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                else:
                    # All retries exhausted
                    return {
                        "reply": "The chatbot is temporarily at capacity. Please try again in a moment. Remember: drink fluids, take paracetamol for fever, and rest. See a doctor if symptoms worsen."
                    }
            else:
                # Other errors - don't retry
                return {
                    "reply": "I'm having trouble right now. Please consult a healthcare professional if you need medical advice."
                }
    
    return {
        "reply": "The chatbot is temporarily unavailable. Please try again or consult a healthcare professional."
    }

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
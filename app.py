from flask import Flask, render_template, request, redirect, session
import pickle
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# Load model
model = pickle.load(open("dengue_model.pkl", "rb"))

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

    pred = model.predict([features])[0]
    prob = model.predict_proba([features])[0][1]

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
    msg = request.json["message"].lower()

    if "fever" in msg:
        reply = "Take paracetamol, drink fluids, and rest."
    elif "platelet" in msg:
        reply = "Papaya leaf juice and coconut water help."
    elif "dengue" in msg:
        reply = "Consult a doctor if symptoms worsen."
    else:
        reply = "Stay hydrated and monitor symptoms."

    return {"reply": reply}

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
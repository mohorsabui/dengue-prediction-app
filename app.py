from flask import Flask, render_template, request
import numpy as np
import pickle

app = Flask(__name__)

# Load model
model = pickle.load(open("dengue_model.pkl", "rb"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
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

        final_features = [features]

        prediction = model.predict(final_features)[0]
        prob = model.predict_proba(final_features)[0][1]
        prob_percent = prob * 100

        # 🎯 Risk Classification
        if prob_percent < 30:
            risk = "Low Risk ✅"
            color = "green"
            advice = "You are safe. Maintain hydration and hygiene."
        elif prob_percent < 70:
            risk = "Medium Risk ⚠️"
            color = "orange"
            advice = "Monitor symptoms and consider consulting a doctor."
        else:
            risk = "High Risk 🔴"
            color = "red"
            advice = "Immediate medical attention is recommended!"

        result = f"{risk} ({prob_percent:.2f}% probability)"

        return render_template(
            "index.html",
            prediction_text=result,
            advice=advice,
            color=color
        )

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
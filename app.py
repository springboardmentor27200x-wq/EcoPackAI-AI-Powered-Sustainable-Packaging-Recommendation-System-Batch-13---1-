from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ================= DATABASE CONFIG =================
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123456789@localhost/ecopackai_db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= DATABASE MODEL =================
class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float)
    strength = db.Column(db.Float)
    cost = db.Column(db.Float)
    co2 = db.Column(db.Float)

# ================= LOAD MODELS =================
cost_model = joblib.load("models/cost_model.pkl")
co2_model = joblib.load("models/co2_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# ================= HOME =================
@app.route("/")
def home():
    return "EcoPackAI Backend Running 🚀"

# ================= UI =================
@app.route("/ui")
def ui():
    return render_template("index.html")

# ================= FEATURE PREPARATION =================
def prepare_features(data):
    try:
        weight = float(data.get("weight", 0))
        strength = float(data.get("strength", 0))

        # Optional inputs (fallback defaults)
        weight_capacity = float(data.get("weight_capacity", 0.8))
        biodegradability = float(data.get("biodegradability", 0.6))
        recyclability = float(data.get("recyclability", 50))

        if weight <= 0 or strength <= 0:
            return None, "Weight and Strength must be positive"

        features = np.array([[
            weight,
            strength,
            weight_capacity,
            biodegradability,
            recyclability
        ]])

        return features, None

    except Exception as e:
        return None, str(e)

# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)

        features, error = prepare_features(data)
        if error:
            return jsonify({"error": error}), 400

        # SCALE INPUT
        features_scaled = scaler.transform(features)

        # PREDICTION
        cost = float(cost_model.predict(features_scaled)[0])
        co2 = float(co2_model.predict(features_scaled)[0])

        # SAVE TO DATABASE
        new_prediction = Prediction(
            weight=float(data.get("weight")),
            strength=float(data.get("strength")),
            cost=cost,
            co2=co2
        )

        db.session.add(new_prediction)
        db.session.commit()

        return jsonify({
            "status": "success",
            "data": {
                "predicted_cost": round(cost, 2),
                "predicted_co2": round(co2, 2)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= HISTORY =================
@app.route("/history", methods=["GET"])
def history():
    try:
        records = Prediction.query.all()

        data = [{
            "weight": r.weight,
            "strength": r.strength,
            "cost": r.cost,
            "co2": r.co2
        } for r in records]

        return jsonify({"status": "success", "data": data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= RECOMMEND =================
@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json(force=True)

        features, error = prepare_features(data)
        if error:
            return jsonify({"error": error}), 400

        features_scaled = scaler.transform(features)

        cost = float(cost_model.predict(features_scaled)[0])
        co2 = float(co2_model.predict(features_scaled)[0])

        # IMPROVED DECISION LOGIC
        if co2 > 80000:
            material = "Recycled Paper"
        elif co2 > 40000:
            material = "Bioplastic"
        else:
            material = "EcoComposite"

        return jsonify({
            "status": "success",
            "data": {
                "recommended_material": material,
                "predicted_cost": round(cost, 2),
                "predicted_co2": round(co2, 2)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= ECO SCORE =================
@app.route("/score", methods=["POST"])
def score():
    try:
        data = request.get_json(force=True)

        cost = float(data.get("cost", 0))
        co2 = float(data.get("co2", 0))

        # ✅ FIXED ECO SCORE (BALANCED)
        eco_score = max(0, 100 - (co2 / 3000 + cost * 0.3))

        return jsonify({
            "status": "success",
            "data": {
                "environment_score": round(eco_score, 2)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
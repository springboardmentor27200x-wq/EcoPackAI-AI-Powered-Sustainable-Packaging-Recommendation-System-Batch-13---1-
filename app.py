from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# ========================
# LOAD MODELS
# ========================
print("Loading models...")

cost_model = joblib.load("models/cost_model.pkl")
co2_model = joblib.load("models/co2_model.pkl")
scaler = joblib.load("models/scaler.pkl")

print("Models Loaded ✅")


# ========================
# DB CONNECTION (CLOUD READY)
# ========================
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            database=os.environ.get("DB_NAME", "Ecopack"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "1234")
        )
        return conn
    except Exception as e:
        print("DB CONNECTION FAILED ❌", e)
        return None


# ========================
# HOME ROUTE
# ========================
@app.route("/")
def home():
    return render_template("index.html")


# ========================
# SECURITY
# ========================
API_KEY = "ecopack123"

def check_key(req):
    return req.headers.get("x-api-key") == API_KEY


# ========================
# RECOMMEND API
# ========================
@app.route("/recommend", methods=["POST"])
def recommend():

    print("🔥 API HIT")

    try:
        # 🔐 API KEY CHECK
        if not check_key(request):
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401

        data = request.json
        print("Incoming Data:", data)

        weight = float(data.get("weight", 1))
        fragility = int(data.get("fragility", 1))
        moisture = int(data.get("moisture", 1))

        conn = get_db_connection()

        # ========================
        # FETCH MATERIALS
        # ========================
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM materials")
            materials = cur.fetchall()
            cur.close()
            conn.close()
            print("Materials from DB:", len(materials))
        else:
            materials = []

        # ========================
        # DEMO BACKUP
        # ========================
        if len(materials) == 0:
            print("Using DEMO DATA ⚠️")
            materials = [
                (1,"Corrugated Box",0.8,9,15,8,85,4),
                (2,"Molded Fiber",0.7,8,12,9,80,3),
                (3,"Bioplastic",0.6,7,10,7,75,5),
                (4,"Recycled Paper",0.75,8.5,13,8.5,82,3.5),
                (5,"Foam Insert",0.9,9.5,18,6,60,5)
            ]

        results = []

        for m in materials:

            material_name = m[1]

            # CO2 Prediction
            X_co2 = [[m[7], m[2], m[5], m[6]]]
            X_co2 = scaler.transform(X_co2)
            co2 = co2_model.predict(X_co2)[0]

            # Cost Prediction
            X_cost = [[m[2], m[3], m[4], m[6], fragility]]
            cost = cost_model.predict(X_cost)[0]

            # Score Calculation
            score = 1 / (abs(cost) + abs(co2) + 1e-6)

            results.append({
                "material": material_name,
                "score": float(score),
                "predicted_cost": float(cost),
                "predicted_co2": float(co2)
            })

        # SORT RESULTS
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        return jsonify({
            "status": "success",
            "top_recommendations": results
        })

    except Exception as e:
        print("❌ ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        })


# ========================
# RUN SERVER (DEPLOY READY)
# ========================
if __name__ == "__main__":
    print("🚀 Starting EcoPackAI Server...")

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
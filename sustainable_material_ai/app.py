from flask import Flask, request, jsonify, render_template
import psycopg2
import pandas as pd
import joblib
from contextlib import contextmanager
import os
app = Flask(__name__)

# --- 1. CONFIGURATION & ASSET LOADING ---
MODELS_PATH = "models/"
import psycopg2
from contextlib import contextmanager

# --- UPDATED DATABASE LOGIC FOR MILESTONE 4 ---

def get_db_connection():
    # Render and Heroku automatically provide this environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # This runs when your app is LIVE on the internet
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        # This runs when you are testing on your LOCAL LAPTOP
        return psycopg2.connect(
            host="localhost",
            database="sustainable_materials_db",
            user="postgres",
            password="nandhu2006", 
            port="5432"
        )

@contextmanager
def get_db_cursor():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def load_assets():
    try:
        cost_model = joblib.load(f"{MODELS_PATH}cost_model.pkl")
        co2_model = joblib.load(f"{MODELS_PATH}co2_model.pkl")
        scaler = joblib.load(f"{MODELS_PATH}scaler.pkl")
        model_columns = joblib.load(f"{MODELS_PATH}model_columns.pkl")
        return cost_model, co2_model, scaler, model_columns
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load ML assets: {e}")
        return None, None, None, None

cost_model, co2_model, scaler, model_columns = load_assets()


# --- 3. ROUTES ---

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add_product", methods=["POST"])
def add_product():
    try:
        data = request.json
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO products 
                (product_name, industry_category, product_weight_kg, 
                 fragility_level, shipping_type, safety_requirement)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data.get("product_name"), data.get("industry_category"),
                data.get("product_weight_kg"), data.get("fragility_level"),
                data.get("shipping_type"), data.get("safety_requirement")
            ))
        return jsonify({"status": "success", "message": "Product stored"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/recommend", methods=["POST"])
def recommend():
    if not cost_model:
        return jsonify({"error": "ML models not loaded"}), 500

    data = request.json
    industry = data.get("industry")
    weight = float(data.get("weight", 0))

    try:
        # 1. Fetch Materials
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM materials")
            cols = [desc[0] for desc in cur.description]
            df = pd.DataFrame(cur.fetchall(), columns=cols)

        if df.empty:
            return jsonify({"message": "No materials in database"}), 404

        # 2. [span_3](start_span)Filter (Product Profiles)[span_3](end_span)
        if industry:
            df = df[df["industry_category"] == industry]
        if weight > 0:
            df = df[df["weight_capacity_kg"] >= weight]

        if df.empty:
            return jsonify([]), 200

        material_names = df["material_name"].values

        # 3. [span_4](start_span)[span_5](start_span)Feature Engineering & Scaling (Milestone 1 & 2 requirements)[span_4](end_span)[span_5](end_span)
        co2_map = {"low": 0.2, "medium": 0.5, "high": 0.8}
        df["co2_numeric"] = df["co2_emission_score"].map(co2_map).fillna(0.5)
        
        # [span_6](start_span)[span_7](start_span)Calculate indices as required by outcomes[span_6](end_span)[span_7](end_span)
        df["co2_impact_index"] = (df["biodegradability_score"] * 0.4 + 
                                  df["recyclability_percent"] * 0.4 - 
                                  df["co2_numeric"] * 0.2)
        
        df["cost_efficiency_index"] = (df["strength_min_mpa"] * 0.5 + 
                                       df["weight_capacity_kg"] * 0.5)

        # [span_8](start_span)Scale numerical features[span_8](end_span)
        num_cols = ["strength_min_mpa", "strength_max_mpa", "weight_capacity_kg", 
                    "biodegradability_score", "recyclability_percent", "co2_numeric"]
        df[num_cols] = scaler.transform(df[num_cols])

        # 4. Prepare for ML
        df_encoded = pd.get_dummies(df, columns=["material_type", "industry_category"])
        df_final = df_encoded.reindex(columns=model_columns, fill_value=0)

        # 5. [span_9](start_span)[span_10](start_span)ML Prediction & Ranking[span_9](end_span)[span_10](end_span)
        cost_preds = cost_model.predict(df_final)
        co2_preds = co2_model.predict(df_final)
        
        result = pd.DataFrame({
            "material_name": material_names,
            "predicted_cost": cost_preds,
            "predicted_co2": co2_preds,
            "biodegradability": df["biodegradability_score"].values
        })

        # [span_11](start_span)Calculate final rank: Lower cost/CO2 + higher biodegradability[span_11](end_span)
        result["rank_score"] = ( (1 - result["predicted_cost"]) * 0.4 + 
                                 (1 - result["predicted_co2"]) * 0.4 + 
                                 result["biodegradability"] * 0.2 )

        result = result.sort_values("rank_score", ascending=False)

        # 6. [span_12](start_span)JSON Response[span_12](end_span)
        return jsonify(result.head(10).to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": f"Recommendation failed: {str(e)}"}), 500

@app.route("/environment_score", methods=["POST"])
def environment_score():
    try:
        data = request.json
        score = (
            float(data["biodegradability"]) * 0.4 +
            float(data["recyclability"]) * 0.4 -
            float(data["co2"]) * 0.2
        )
        return jsonify({"environment_score": round(score, 4)})
    except Exception as e:
        return jsonify({"error": "Invalid input for score calculation"}), 400

if __name__ == "__main__":
    app.run(debug=True)

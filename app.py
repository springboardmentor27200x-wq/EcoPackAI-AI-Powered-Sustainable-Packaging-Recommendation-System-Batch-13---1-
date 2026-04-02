from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
from io import BytesIO
import os
import sys
from datetime import datetime
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

try:
    import mysql.connector
except ModuleNotFoundError:
    mysql = None

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ModuleNotFoundError:
    psycopg2 = None
    RealDictCursor = None

try:
    import joblib
except ModuleNotFoundError:
    joblib = None

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
except ModuleNotFoundError:
    colors = None
    A4 = None
    ParagraphStyle = None
    getSampleStyleSheet = None
    Paragraph = None
    SimpleDocTemplate = None
    Spacer = None
    Table = None
    TableStyle = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.getenv("SECRET_KEY", "ecopackai-dev-secret-key")
MODEL_DIR = os.path.join(BASE_DIR, "models")
COST_MODEL_PATH = os.path.join(MODEL_DIR, "cost_model.pkl")
CO2_MODEL_PATH = os.path.join(MODEL_DIR, "co2_model.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "feature_names.pkl")
MODEL_CACHE = {"cost": None, "co2": None, "features": None, "loaded": False}

DEFAULT_MATERIALS = [
    {
        "name": "Corrugated Cardboard",
        "type": "Paper",
        "icon": "&#128230;",
        "description": "Recyclable, strong, and widely used for shipping boxes",
        "strength": 85,
        "strength_raw": 8.5,
        "weight_capacity": 10.0,
        "biodegradability": 95,
        "recyclability": 92,
        "co2": "0.8 kg/kg",
        "cost": "$0.45/kg",
        "cost_value": 0.45,
        "co2_value": 0.8,
        "suitability_score": 3.4,
        "best_for": ["Electronics", "Furniture", "Toys"]
    },
    {
        "name": "Molded Pulp",
        "type": "Paper",
        "icon": "&#129370;",
        "description": "Made from recycled paper, perfect for protective inserts",
        "strength": 70,
        "strength_raw": 7.0,
        "weight_capacity": 8.0,
        "biodegradability": 98,
        "recyclability": 95,
        "co2": "0.5 kg/kg",
        "cost": "$0.35/kg",
        "cost_value": 0.35,
        "co2_value": 0.5,
        "suitability_score": 3.7,
        "best_for": ["Electronics", "Food", "Cosmetics"]
    },
    {
        "name": "PLA Bioplastic",
        "type": "Bioplastic",
        "icon": "&#127805;",
        "description": "Plant-based plastic from corn starch, compostable",
        "strength": 75,
        "strength_raw": 7.5,
        "weight_capacity": 6.0,
        "biodegradability": 85,
        "recyclability": 70,
        "co2": "1.2 kg/kg",
        "cost": "$1.80/kg",
        "cost_value": 1.8,
        "co2_value": 1.2,
        "suitability_score": 3.1,
        "best_for": ["Food", "Cosmetics", "Pharma"]
    }
]

fallback_history = []
MATERIAL_ICONS = {
    "paper": "&#128230;",
    "bioplastic": "&#127805;",
    "plant": "&#127807;",
    "recycled": "&#9851;",
    "glass": "&#129718;",
    "plastic": "&#129388;",
    "biodegradable": "&#127793;",
    "eco-friendly composite": "&#127793;",
    "recyclable polymer": "&#9851;"
}
FRAGILITY_MAP = {"low": 2.0, "medium": 5.0, "high": 9.0}
STRENGTH_MAP = {"low": 3.0, "medium": 6.0, "high": 9.0}
SHIPPING_MAP = {"standard": 1.0, "protective": 1.1, "express": 1.15, "international": 1.25}
DISPLAY_NAME_MAP = {
    "carton": "Corrugated Cardboard",
    "vidrio": "Glass Packaging",
    "plastico": "Bioplastic",
    "metal": "Metal Packaging",
}


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def get_db_engine():
    return os.getenv("DB_ENGINE", "mysql").strip().lower()


def create_cursor(connection, dictionary=False):
    if get_db_engine() == "postgres":
        if dictionary and RealDictCursor is not None:
            return connection.cursor(cursor_factory=RealDictCursor)
        return connection.cursor()
    if dictionary:
        return connection.cursor(dictionary=True)
    return connection.cursor()


def get_db_connection():
    try:
        engine = get_db_engine()
        if engine == "postgres":
            if psycopg2 is None:
                return None

            config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", ""),
                "dbname": os.getenv("DB_NAME", "ecopackai_db"),
                "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
                "sslmode": os.getenv("DB_SSL_MODE", "prefer"),
            }
            return psycopg2.connect(**config)

        if mysql is None:
            return None

        config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", "adi@2400"),
            "database": os.getenv("DB_NAME", "ecopackai_db"),
            "connection_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
        }

        if os.getenv("DB_SSL_DISABLED", "false").strip().lower() == "true":
            config["ssl_disabled"] = True
        else:
            config["ssl_disabled"] = False

            ssl_ca = os.getenv("DB_SSL_CA", "").strip()
            if ssl_ca:
                config["ssl_ca"] = ssl_ca

            if os.getenv("DB_SSL_VERIFY_CERT", "false").strip().lower() == "true":
                config["ssl_verify_cert"] = True

            if os.getenv("DB_SSL_VERIFY_IDENTITY", "false").strip().lower() == "true":
                config["ssl_verify_identity"] = True

        return mysql.connector.connect(**config)
    except Exception as error:
        print(f"[EcoPackAI][DB] Connection failed: {error}", file=sys.stderr)
        return None


def load_models():
    if MODEL_CACHE["loaded"]:
        return MODEL_CACHE["cost"], MODEL_CACHE["co2"], MODEL_CACHE["features"]

    MODEL_CACHE["loaded"] = True
    if joblib is None:
        return None, None, None

    try:
        MODEL_CACHE["cost"] = joblib.load(COST_MODEL_PATH)
    except Exception:
        MODEL_CACHE["cost"] = None

    try:
        MODEL_CACHE["co2"] = joblib.load(CO2_MODEL_PATH)
    except Exception:
        MODEL_CACHE["co2"] = None

    try:
        MODEL_CACHE["features"] = joblib.load(FEATURES_PATH)
    except Exception:
        MODEL_CACHE["features"] = None

    return MODEL_CACHE["cost"], MODEL_CACHE["co2"], MODEL_CACHE["features"]


def material_icon(material_type):
    return MATERIAL_ICONS.get((material_type or "").lower(), "&#127795;")


def display_material_name(name):
    key = (name or "").strip().lower()
    return DISPLAY_NAME_MAP.get(key, name)


def infer_material_type(name, material_type):
    value = (material_type or "").strip()
    if value:
        return value.title()

    lowered = (name or "").lower()
    if "carton" in lowered:
        return "Paper"
    if "plastico" in lowered or "plastic" in lowered:
        return "Bioplastic"
    if "vidrio" in lowered:
        return "Glass"
    if "metal" in lowered:
        return "Metal"
    if any(term in lowered for term in ["paper", "cardboard", "pulp"]):
        return "Paper"
    if any(term in lowered for term in ["plastic", "pla", "foam"]):
        return "Bioplastic"
    if "glass" in lowered:
        return "Glass"
    if "recycled" in lowered:
        return "Recycled"
    return "Plant"


def strength_band(required_strength):
    value = (required_strength or "medium").strip().lower()
    if value == "low":
        return (1, 4)
    if value == "high":
        return (8, 10)
    return (5, 7)


def strength_numeric(required_strength):
    return STRENGTH_MAP.get((required_strength or "medium").strip().lower(), 6.0)


def shipping_numeric(shipping_type):
    return SHIPPING_MAP.get((shipping_type or "standard").strip().lower(), 1.0)


def infer_shipping_type(fragility_level, category):
    fragility = (fragility_level or "").strip().lower()
    category_value = (category or "").strip().lower()
    if fragility == "high":
        return "Protective"
    if category_value in {"electronics", "pharma", "cosmetics"}:
        return "Express"
    return "Standard"


def category_tags(category):
    value = (category or "").strip().lower()
    mapping = {
        "electronics": ["Electronics", "Toys", "Furniture"],
        "food": ["Food", "Cosmetics"],
        "cosmetics": ["Cosmetics", "Food"],
        "clothing": ["Clothing", "Cosmetics"],
        "furniture": ["Furniture", "Electronics"],
        "pharma": ["Pharma", "Cosmetics"],
        "toys": ["Toys", "Electronics"],
        "home appliances": ["Electronics", "Furniture"]
    }
    return mapping.get(value, [category.title() if category else "General", "Electronics", "Food"])


def best_for_tags(material_name, material_type):
    lowered = (material_name or "").strip().lower()
    if "carton" in lowered:
        return ["Electronics", "Furniture", "Toys", "Food", "Home Appliances"]
    if "plastico" in lowered or "plastic" in lowered:
        return ["Food", "Cosmetics", "Pharma"]
    if "vidrio" in lowered:
        return ["Cosmetics", "Food", "Pharma"]
    if "metal" in lowered:
        return ["Electronics", "Furniture", "Pharma", "Industrial"]
    if "garbage" in lowered:
        return ["General"]
    pretty_type = material_type.title() if material_type else "General"
    return [pretty_type, "Electronics", "Food"]


def fetch_materials(limit=9):
    connection = get_db_connection()
    if not connection:
        return DEFAULT_MATERIALS

    cursor = create_cursor(connection)
    try:
        cursor.execute(
            """
            SELECT material,
                   AVG(strength) AS strength,
                   AVG(weight_capacity) AS weight_capacity,
                   AVG(biodegradability) AS biodegradability,
                   AVG(co2_score) AS co2_score,
                   AVG(cost) AS cost,
                   AVG(recyclability) AS recyclability
            FROM final_material_dataset
            GROUP BY material
            """,
        )
        rows = cursor.fetchall()
    except Exception:
        rows = []
    finally:
        cursor.close()
        connection.close()

    if not rows:
        return DEFAULT_MATERIALS

    materials = []
    for row in rows:
        name, strength, weight_capacity, biodegradability, co2_score, cost_per_unit, recyclability = row
        if (name or "").strip().lower() == "garbage classification":
            continue
        pretty_type = infer_material_type(name, "")
        display_name = display_material_name(name)
        suitability_score = round(
            (float(biodegradability or 0) * 0.4)
            + (float(recyclability or 0) * 0.3)
            + (max(0, 100 - (float(co2_score or 0) * 8)) * 0.2)
            + (float(strength or 0) * 2),
            2,
        )
        materials.append(
            {
                "name": display_name,
                "source_name": name,
                "type": pretty_type,
                "icon": material_icon(pretty_type),
                "description": "AI-ranked sustainable packaging option based on your material dataset.",
                "strength": round(float(strength or 0) * 10),
                "strength_raw": float(strength or 0),
                "weight_capacity": float(weight_capacity or 0),
                "biodegradability": round(float(biodegradability or 0) * 10),
                "recyclability": round(float(recyclability or 0)),
                "co2": f"{float(co2_score or 0):.2f} kg/kg",
                "co2_value": float(co2_score or 0),
                "cost": f"${float(cost_per_unit or 0):.2f}/kg",
                "cost_value": float(cost_per_unit or 0),
                "suitability_score": float(suitability_score or 0),
                "best_for": best_for_tags(name, pretty_type)
            }
        )
    materials.sort(key=lambda item: item["suitability_score"], reverse=True)
    return materials[:limit]


def fetch_product_profile(product_name, category):
    default_profile = {
        "matched_product": product_name or "Custom Product",
        "required_strength": "Medium",
        "shipping_type": "Standard",
        "dataset_weight": None
    }

    connection = get_db_connection()
    if not connection:
        return default_profile

    cursor = create_cursor(connection, dictionary=True)
    try:
        if product_name:
            cursor.execute(
                """
                SELECT product_name, product_category, product_weight_kg, fragility_level, required_strength
                FROM final_product_dataset
                WHERE LOWER(product_name) = LOWER(%s)
                LIMIT 1
                """,
                (product_name,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "matched_product": row["product_name"],
                    "required_strength": row.get("required_strength") or "Medium",
                    "shipping_type": infer_shipping_type(row.get("fragility_level"), row.get("product_category")),
                    "dataset_weight": float(row.get("product_weight_kg") or 0)
                }

        if category:
            cursor.execute(
                """
                SELECT product_name, product_category, product_weight_kg, fragility_level, required_strength
                FROM final_product_dataset
                WHERE LOWER(product_category) = LOWER(%s)
                """,
                (category,)
            )
            rows = cursor.fetchall()
            if rows:
                avg_weight = sum(float(row.get("product_weight_kg") or 0) for row in rows) / len(rows)
                fragility_counts = {}
                strength_counts = {}
                for row in rows:
                    fragility_key = (row.get("fragility_level") or "Medium").strip().title()
                    strength_key = (row.get("required_strength") or "Medium").strip().title()
                    fragility_counts[fragility_key] = fragility_counts.get(fragility_key, 0) + 1
                    strength_counts[strength_key] = strength_counts.get(strength_key, 0) + 1

                common_fragility = max(fragility_counts, key=fragility_counts.get)
                common_strength = max(strength_counts, key=strength_counts.get)
                return {
                    "matched_product": category.title(),
                    "required_strength": common_strength,
                    "shipping_type": infer_shipping_type(common_fragility, category),
                    "dataset_weight": float(avg_weight or 0)
                }
    except Exception:
        pass
    finally:
        cursor.close()
        connection.close()

    return default_profile


def score_material_options(category, weight, fragility_label, priority, product_profile):
    required_strength = product_profile.get("required_strength", "Medium")
    shipping_type = product_profile.get("shipping_type", "Standard")
    min_strength, max_strength = strength_band(required_strength)
    tags = category_tags(category)
    category_value = (category or "").strip().lower()
    materials = fetch_materials(limit=12)

    scored = []
    for material in materials:
        strength_raw = material.get("strength_raw", material["strength"] / 10)
        strength_fit = 20 if min_strength <= strength_raw <= max_strength else max(0, 14 - abs(strength_raw - ((min_strength + max_strength) / 2)) * 4)
        capacity_fit = 18 if material["weight_capacity"] >= weight else max(0, 18 - (weight - material["weight_capacity"]) * 2)
        eco_score = (material["biodegradability"] * 0.45) + (material["recyclability"] * 0.25) + (max(0, 100 - material["co2_value"] * 12) * 0.30)
        cost_score = max(0, 100 - material["cost_value"] * 18)
        category_bonus = 10 if any(tag in material["best_for"] for tag in tags) else 0
        shipping_bonus = 6 if shipping_type.lower() in ["international", "express", "protective"] and strength_raw >= 7 else 2
        fragility_bonus = 6 if fragility_label.lower() == "high" and strength_raw >= 8 else 3

        domain_bonus = 0
        source_name = (material.get("source_name") or material["name"]).strip().lower()
        if category_value in ["electronics", "home appliances"]:
            if "carton" in source_name:
                domain_bonus += 12
            if "metal" in source_name and weight <= 10:
                domain_bonus += 4
            if weight > 15 and "carton" in source_name:
                domain_bonus += 10
        elif category_value == "food":
            if "carton" in source_name:
                domain_bonus += 8
            if "plastico" in source_name or "vidrio" in source_name:
                domain_bonus += 6
        elif category_value == "cosmetics":
            if "vidrio" in source_name:
                domain_bonus += 12
            if "plastico" in source_name:
                domain_bonus += 8
        elif category_value == "pharma":
            if "vidrio" in source_name:
                domain_bonus += 10
            if "plastico" in source_name:
                domain_bonus += 7
        elif category_value in ["furniture", "industrial"]:
            if "carton" in source_name:
                domain_bonus += 10
            if "metal" in source_name:
                domain_bonus += 6

        total = (eco_score * (priority / 10.0)) + (cost_score * (1 - (priority / 10.0))) + strength_fit + capacity_fit + category_bonus + shipping_bonus + fragility_bonus + domain_bonus + material["suitability_score"]
        scored.append((round(total, 2), material))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored, required_strength, shipping_type


def choose_best_material(category, weight, fragility_label, priority, product_profile):
    scored, required_strength, shipping_type = score_material_options(
        category, weight, fragility_label, priority, product_profile
    )
    return scored[0], required_strength, shipping_type


def build_feature_frame(weight, fragility_score, required_strength, shipping_type, best_material, feature_names):
    feature_values = {
        "product_weight": float(weight),
        "fragility_score": float(fragility_score),
        "required_strength_score": float(strength_numeric(required_strength)),
        "shipping_score": float(shipping_numeric(shipping_type)),
        "material_strength": float(best_material.get("strength_raw", best_material["strength"] / 10)),
        "weight_capacity": float(best_material.get("weight_capacity", 0)),
        "biodegradability_score": float(best_material.get("biodegradability", 0) / 10),
        "co2_emission_score": float(best_material.get("co2_value", 0)),
        "cost_per_unit": float(best_material.get("cost_value", 0)),
        "recyclability_percent": float(best_material.get("recyclability", 0)),
        "suitability_score": float(best_material.get("suitability_score", 0))
    }

    if pd is None:
        return None

    ordered = {name: feature_values[name] for name in feature_names}
    return pd.DataFrame([ordered])


def predict_with_models(weight, fragility_score, priority, required_strength, shipping_type, best_material):
    cost_model, co2_model, feature_names = load_models()

    if pd is not None and cost_model is not None and co2_model is not None and feature_names:
        try:
            feature_frame = build_feature_frame(weight, fragility_score, required_strength, shipping_type, best_material, feature_names)
            predicted_cost = float(cost_model.predict(feature_frame)[0])
            predicted_co2 = float(co2_model.predict(feature_frame)[0])
        except Exception:
            predicted_cost = (weight * best_material["cost_value"] * 4.0) + fragility_score
            predicted_co2 = (weight * best_material["co2_value"] * 1.1) + (fragility_score * 0.5)
    else:
        predicted_cost = (weight * best_material["cost_value"] * 4.0) + fragility_score
        predicted_co2 = (weight * best_material["co2_value"] * 1.1) + (fragility_score * 0.5)

    priority_factor = 1.0 - ((priority - 5.0) / 50.0)
    predicted_cost = round(max(0.1, predicted_cost * priority_factor), 2)
    predicted_co2 = round(max(0.1, predicted_co2 * (2.0 - priority_factor)), 2)
    environmental_score = round((best_material["suitability_score"] * 10 + max(0, 100 - predicted_co2)) / 2, 2)
    return predicted_cost, predicted_co2, environmental_score


def save_product(product_name, category, weight, fragility, shipping_type):
    connection = get_db_connection()
    if not connection:
        return

    cursor = create_cursor(connection)
    try:
        cursor.execute(
            "INSERT INTO products(product_name, category, weight, fragility, shipping_type) VALUES (%s, %s, %s, %s, %s)",
            (product_name, category, weight, fragility, shipping_type)
        )
        connection.commit()
    except Exception:
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def save_history(weight, fragility_score, material, co2, cost):
    connection = get_db_connection()
    if not connection:
        fallback_history.append((len(fallback_history) + 1, weight, fragility_score, material, round(co2, 2), round(cost, 2)))
        return

    cursor = create_cursor(connection)
    try:
        cursor.execute(
            "INSERT INTO history(weight, fragility, material, co2, cost) VALUES (%s, %s, %s, %s, %s)",
            (weight, fragility_score, material, co2, cost)
        )
        connection.commit()
    except Exception:
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def save_recommendation(product_name, material, co2_saved, cost_saved):
    connection = get_db_connection()
    if not connection:
        return

    cursor = create_cursor(connection)
    try:
        cursor.execute(
            "INSERT INTO recommendations(product_name, material, co2_saved, cost_saved) VALUES (%s, %s, %s, %s)",
            (product_name, material, co2_saved, cost_saved)
        )
        connection.commit()
    except Exception:
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def save_prediction(best_material, predicted_cost, predicted_co2, environmental_score, recommendation_text):
    connection = get_db_connection()
    if not connection:
        return

    cursor = create_cursor(connection)
    try:
        cursor.execute(
            """
            INSERT INTO predictions(strength, weight_capacity, recyclability, biodegradability, material, predicted_cost, predicted_co2, environmental_score, recommendation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                best_material.get("strength_raw", best_material["strength"] / 10),
                best_material.get("weight_capacity", 0),
                best_material.get("recyclability", 0),
                best_material.get("biodegradability", 0) / 10,
                best_material["name"],
                predicted_cost,
                predicted_co2,
                environmental_score,
                recommendation_text
            )
        )
        connection.commit()
    except Exception:
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def create_user(name, email, password):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed.", None

    cursor = create_cursor(connection, dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return False, "An account with this email already exists.", None

        hashed_password = generate_password_hash(password)
        if get_db_engine() == "postgres":
            cursor.execute(
                "INSERT INTO users(name, email, password) VALUES (%s, %s, %s) RETURNING id",
                (name, email, hashed_password),
            )
            new_user_id = cursor.fetchone()["id"]
        else:
            cursor.execute(
                "INSERT INTO users(name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_password),
            )
            new_user_id = cursor.lastrowid
        connection.commit()
        return True, "Account created successfully.", new_user_id
    except Exception as error:
        print(f"[EcoPackAI][Auth] Signup failed for {email}: {error}", file=sys.stderr)
        connection.rollback()
        return False, "Unable to create account right now.", None
    finally:
        cursor.close()
        connection.close()


def authenticate_user(email, password):
    connection = get_db_connection()
    if not connection:
        print(f"[EcoPackAI][Auth] Login blocked because database connection is unavailable for {email}.", file=sys.stderr)
        return None

    cursor = create_cursor(connection, dictionary=True)
    try:
        cursor.execute("SELECT id, name, email, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            stored_password = user["password"] or ""
            if stored_password == password:
                return user
            if stored_password.startswith("pbkdf2:") or stored_password.startswith("scrypt:"):
                if check_password_hash(stored_password, password):
                    return user
        return None
    finally:
        cursor.close()
        connection.close()


def collect_analytics_data():
    connection = get_db_connection()
    total = 0
    avg_co2 = 0
    avg_cost = 0
    labels = []
    values = []
    recent_history = []
    trend_points = []

    if connection:
        cursor = create_cursor(connection)
        try:
            cursor.execute("SELECT COUNT(*) FROM history")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(co2), AVG(cost) FROM history")
            avg = cursor.fetchone()
            avg_co2 = round(avg[0], 2) if avg and avg[0] else 0
            avg_cost = round(avg[1], 2) if avg and avg[1] else 0

            cursor.execute("SELECT material, COUNT(*) FROM history GROUP BY material ORDER BY COUNT(*) DESC")
            material_data = cursor.fetchall()
            labels = [row[0] for row in material_data]
            values = [row[1] for row in material_data]

            cursor.execute("SELECT material, co2, cost FROM history ORDER BY id DESC LIMIT 5")
            recent_history = cursor.fetchall()

            cursor.execute("SELECT id, weight, co2 FROM history ORDER BY id ASC")
            trend_points = cursor.fetchall()
        finally:
            cursor.close()
            connection.close()
    else:
        total = len(fallback_history)
        avg_co2 = round(sum(row[4] for row in fallback_history) / total, 2) if total else 0
        avg_cost = round(sum(row[5] for row in fallback_history) / total, 2) if total else 0
        counts = {}
        for row in fallback_history:
            counts[row[3]] = counts.get(row[3], 0) + 1
        labels = list(counts.keys())
        values = list(counts.values())
        recent_history = [(row[3], row[4], row[5]) for row in fallback_history[-5:]][::-1]
        trend_points = [(row[0], row[1], row[4]) for row in fallback_history]

    if not labels:
        labels = ["Corrugated Cardboard", "Molded Pulp", "PLA Bioplastic", "Mushroom Packaging", "Other"]
        values = [7, 5, 4, 3, 2]

    original_co2 = avg_co2 + 5 if avg_co2 else 25
    original_cost = avg_cost + 10 if avg_cost else 20
    co2_saved = round(((original_co2 - avg_co2) / original_co2) * 100, 2) if original_co2 else 0
    cost_saved = round(((original_cost - avg_cost) / original_cost) * 100, 2) if original_cost else 0

    normalized_trend = []
    for entry in trend_points:
        record_id, weight_value, co2_value = entry
        baseline = float(weight_value or 0) * 2.0
        if baseline <= 0:
            continue
        reduction_pct = round(max(0, ((baseline - float(co2_value or 0)) / baseline) * 100), 2)
        normalized_trend.append((record_id, reduction_pct))

    normalized_trend = normalized_trend[-7:]
    trend_labels = [f"Run {record_id}" for record_id, _ in normalized_trend]
    trend_values = [reduction for _, reduction in normalized_trend]
    if not trend_labels:
        trend_labels = ["Run 1", "Run 2", "Run 3", "Run 4", "Run 5", "Run 6"]
        trend_values = [18, 24, 31, 39, 44, 49]

    normalized_history = []
    for row in recent_history:
        material, co2_value, cost_value = row
        normalized_history.append(
            {
                "material": str(material),
                "co2": round(float(co2_value or 0), 2),
                "cost": round(float(cost_value or 0), 2),
            }
        )

    return {
        "total": total,
        "avg_co2": avg_co2,
        "avg_cost": avg_cost,
        "labels": labels,
        "values": values,
        "co2_saved": co2_saved,
        "cost_saved": cost_saved,
        "recent_history": normalized_history,
        "trend_labels": trend_labels,
        "trend_values": trend_values,
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        flash("You are already logged in.", "success")
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = authenticate_user(email, password)
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Welcome back!", "success")
            return redirect(url_for("home"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        flash("You are already logged in.", "success")
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "warning")
        else:
            success, message, user_id = create_user(name, email, password)
            flash(message, "success" if success else "danger")
            if success:
                session["user_id"] = user_id
                session["user_name"] = name
                flash("Your account is ready. Welcome to EcoPackAI!", "success")
                return redirect(url_for("home"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    return render_template("dashboard.html", active_page="dashboard")


@app.route("/materials")
@login_required
def materials_page():
    return render_template("materials.html", active_page="materials", materials=fetch_materials())


@app.route("/recommend", methods=["GET", "POST"])
@login_required
def recommend():
    result = None
    alternatives = []

    if request.method == "POST":
        product_name = request.form.get("product_name", "Custom Product")
        category = request.form.get("category", "Electronics")
        weight = float(request.form["weight"])
        fragility_score = float(request.form["fragility"])
        priority = float(request.form["priority"])
        fragility_label = {2.0: "Low", 5.0: "Medium", 9.0: "High"}.get(fragility_score, "Medium")

        product_profile = fetch_product_profile(product_name, category)
        if request.form.get("shipping"):
            product_profile["shipping_type"] = request.form.get("shipping")

        scored_materials, required_strength, shipping_type = score_material_options(
            category, weight, fragility_label, priority, product_profile
        )
        rank_score, best_material = scored_materials[0]

        final_cost, final_co2, environmental_score = predict_with_models(
            weight, fragility_score, priority, required_strength, shipping_type, best_material
        )
        co2_saved = round(max(0, (weight * 2.0) - final_co2), 2)
        cost_saved = round(max(0, (weight * 2.5) - final_cost), 2)
        recommendation_text = f"Use {best_material['name']} for {product_name} with {required_strength} strength need and {shipping_type} shipping."
        eco_priority = "Sustainability-first" if priority >= 7 else "Balanced" if priority >= 4 else "Cost-first"

        result_reasons = [
            f"Matched the {required_strength.lower()} strength requirement for {category.lower()} packaging.",
            f"Handled {shipping_type.lower()} shipping needs with a strong weight-capacity fit.",
            f"Balanced your {eco_priority.lower()} priority using cost, CO2, and recyclability signals."
        ]

        result = {
            "material": best_material["name"],
            "co2": final_co2,
            "cost": final_cost,
            "rank_score": rank_score,
            "priority": int(priority),
            "shipping": shipping_type,
            "required_strength": required_strength,
            "matched_product": product_profile.get("matched_product", product_name),
            "environmental_score": environmental_score,
            "eco_priority": eco_priority,
            "description": best_material.get("description", ""),
            "best_for": best_material.get("best_for", []),
            "reasons": result_reasons
        }

        for alt_score, alt_material in scored_materials[1:4]:
            alternatives.append(
                {
                    "material": alt_material["name"],
                    "score": alt_score,
                    "co2": round(float(alt_material.get("co2_value", 0)), 2),
                    "cost": round(float(alt_material.get("cost_value", 0)), 2),
                    "type": alt_material.get("type", "General"),
                }
            )

        save_product(product_name, category, weight, fragility_label, shipping_type)
        save_history(weight, fragility_score, best_material["name"], final_co2, final_cost)
        save_recommendation(product_name, best_material["name"], co2_saved, cost_saved)
        save_prediction(best_material, final_cost, final_co2, environmental_score, recommendation_text)

    return render_template(
        "recommend.html",
        active_page="recommendation",
        result=result,
        alternatives=alternatives,
    )


@app.route("/history")
@login_required
def history():
    connection = get_db_connection()
    if connection:
        cursor = create_cursor(connection)
        cursor.execute("SELECT * FROM history ORDER BY id DESC")
        data = cursor.fetchall()
        cursor.close()
        connection.close()
    else:
        data = fallback_history

    return render_template("history.html", active_page="history", data=data)


@app.route("/analytics")
@login_required
def analytics():
    analytics_data = collect_analytics_data()
    return render_template("analytics.html", active_page="analytics", **analytics_data)


@app.route("/analytics/export-pdf")
@login_required
def export_analytics_pdf():
    global colors, A4, ParagraphStyle, getSampleStyleSheet, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    if SimpleDocTemplate is None:
        try:
            from reportlab.lib import colors as rl_colors
            from reportlab.lib.pagesizes import A4 as rl_a4
            from reportlab.lib.styles import ParagraphStyle as rl_paragraph_style, getSampleStyleSheet as rl_get_styles
            from reportlab.platypus import Paragraph as rl_paragraph, SimpleDocTemplate as rl_doc, Spacer as rl_spacer, Table as rl_table, TableStyle as rl_table_style

            colors = rl_colors
            A4 = rl_a4
            ParagraphStyle = rl_paragraph_style
            getSampleStyleSheet = rl_get_styles
            Paragraph = rl_paragraph
            SimpleDocTemplate = rl_doc
            Spacer = rl_spacer
            Table = rl_table
            TableStyle = rl_table_style
        except ModuleNotFoundError:
            flash(
                f"PDF export still cannot find reportlab in this Python: {sys.executable}",
                "warning",
            )
            return redirect(url_for("analytics"))

    analytics_data = collect_analytics_data()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "EcoTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#165e45"),
        spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "EcoSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#6f7f74"),
        spaceAfter=18,
    )
    section_style = ParagraphStyle(
        "EcoSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#165e45"),
        spaceBefore=8,
        spaceAfter=10,
    )

    story = [
        Paragraph("EcoPackAI Sustainability Report", title_style),
        Paragraph(
            f"Generated for {session.get('user_name', 'User')} from the BI Analytics dashboard.",
            subtitle_style,
        ),
    ]

    summary_rows = [
        ["Metric", "Value"],
        ["Total recommendations", str(analytics_data["total"])],
        ["Average CO2 impact", f'{analytics_data["avg_co2"]} kg'],
        ["Average cost", f'${analytics_data["avg_cost"]}'],
        ["CO2 savings", f'{analytics_data["co2_saved"]}%'],
        ["Cost savings", f'{analytics_data["cost_saved"]}%'],
    ]
    summary_table = Table(summary_rows, colWidths=[220, 220])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#165e45")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f6fbf7")),
                ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#dce9df")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f6fbf7"), colors.white]),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend([Paragraph("Summary", section_style), summary_table, Spacer(1, 18)])

    distribution_rows = [["Material", "Recommendations"]]
    for label, value in zip(analytics_data["labels"], analytics_data["values"]):
        distribution_rows.append([str(label), str(value)])
    distribution_table = Table(distribution_rows, colWidths=[320, 120])
    distribution_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#28c85d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#dce9df")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6fbf7")]),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend([Paragraph("Material Distribution", section_style), distribution_table, Spacer(1, 18)])

    if analytics_data["recent_history"]:
        history_rows = [["Material", "CO2", "Cost"]]
        for row in analytics_data["recent_history"]:
            history_rows.append([row["material"], f'{float(row["co2"]):.2f} kg', f'${float(row["cost"]):.2f}'])
        history_table = Table(history_rows, colWidths=[240, 100, 100])
        history_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef7f1")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#165e45")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#dce9df")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfdfb")]),
                    ("PADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.extend([Paragraph("Recent Recommendations", section_style), history_table])

    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="EcoPackAI_Analytics_Report.pdf",
        mimetype="application/pdf",
    )


@app.route("/analytics/export-excel")
@login_required
def export_analytics_excel():
    if pd is None:
        flash("Excel export needs pandas and openpyxl installed.", "warning")
        return redirect(url_for("analytics"))

    analytics_data = collect_analytics_data()
    buffer = BytesIO()

    try:
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            pd.DataFrame(
                [
                    {"metric": "Total recommendations", "value": analytics_data["total"]},
                    {"metric": "Average CO2 impact (kg)", "value": analytics_data["avg_co2"]},
                    {"metric": "Average cost", "value": analytics_data["avg_cost"]},
                    {"metric": "CO2 savings (%)", "value": analytics_data["co2_saved"]},
                    {"metric": "Cost savings (%)", "value": analytics_data["cost_saved"]},
                ]
            ).to_excel(writer, sheet_name="Summary", index=False)

            pd.DataFrame(
                {"material": analytics_data["labels"], "recommendations": analytics_data["values"]}
            ).to_excel(writer, sheet_name="Material Distribution", index=False)

            pd.DataFrame(
                {"period": analytics_data["trend_labels"], "recommendations": analytics_data["trend_values"]}
            ).to_excel(writer, sheet_name="Trend", index=False)

            pd.DataFrame(analytics_data["recent_history"]).to_excel(writer, sheet_name="Recent History", index=False)
    except Exception:
        flash("Excel export is unavailable until openpyxl is installed in this environment.", "warning")
        return redirect(url_for("analytics"))

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="EcoPackAI_Analytics_Report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    print(f"EcoPackAI starting with Python: {sys.executable}")
    print(f"ReportLab available: {'yes' if SimpleDocTemplate is not None else 'no'}")
    app.run(debug=True)

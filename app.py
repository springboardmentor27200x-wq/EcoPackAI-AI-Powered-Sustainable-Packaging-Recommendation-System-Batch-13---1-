from flask import Flask, render_template, request
import mysql.connector
import os

app = Flask(__name__)

# =========================
# DATABASE CONNECTION
# =========================

db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "adi@2400"),
    database=os.getenv("DB_NAME", "ecopackai_db")
)

cursor = db.cursor()

materials = ["Recycled Paper", "Biodegradable Plastic", "Cardboard", "Mushroom Packaging"]

# =========================
# DASHBOARD
# =========================
@app.route("/")
def home():
    return render_template("dashboard.html")

# =========================
# RECOMMENDATION
# =========================
@app.route("/recommend", methods=["GET", "POST"])
def recommend():

    result = None

    if request.method == "POST":

        weight = float(request.form["weight"])
        fragility = float(request.form["fragility"])
        priority = float(request.form["priority"])

        # AI LOGIC
        co2 = (weight * 2.5) + (fragility * 1.2)
        cost = (weight * 4.0) + (fragility * 2.0)

        score = (co2 * priority) + cost
        best_material = materials[int(score) % 4]

        cursor.execute(
            "INSERT INTO history(weight,fragility,material,co2,cost) VALUES(%s,%s,%s,%s,%s)",
            (weight, fragility, best_material, co2, cost)
        )
        db.commit()

        result = {
            "material": best_material,
            "co2": round(co2, 2),
            "cost": round(cost, 2)
        }

    return render_template("recommend.html", result=result)

# =========================
# HISTORY
# =========================
@app.route("/history")
def history():
    cursor.execute("SELECT * FROM history")
    data = cursor.fetchall()
    return render_template("history.html", data=data)

# =========================
# ANALYTICS (BUSINESS DASHBOARD ⭐)
# =========================
@app.route("/analytics")
def analytics():

    # TOTAL
    cursor.execute("SELECT COUNT(*) FROM history")
    total = cursor.fetchone()[0]

    # AVG VALUES
    cursor.execute("SELECT AVG(co2), AVG(cost) FROM history")
    avg = cursor.fetchone()

    avg_co2 = round(avg[0], 2) if avg[0] else 0
    avg_cost = round(avg[1], 2) if avg[1] else 0

    # MATERIAL USAGE
    cursor.execute("SELECT material, COUNT(*) FROM history GROUP BY material")
    material_data = cursor.fetchall()

    labels = [row[0] for row in material_data]
    values = [row[1] for row in material_data]

    # SAVINGS CALCULATION ⭐
    original_co2 = avg_co2 + 5
    original_cost = avg_cost + 10

    co2_saved = round(((original_co2 - avg_co2) / original_co2) * 100, 2) if avg_co2 else 0
    cost_saved = round(((original_cost - avg_cost) / original_cost) * 100, 2) if avg_cost else 0

    return render_template(
        "analytics.html",
        total=total,
        avg_co2=avg_co2,
        avg_cost=avg_cost,
        labels=labels,
        values=values,
        co2_saved=co2_saved,
        cost_saved=cost_saved
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
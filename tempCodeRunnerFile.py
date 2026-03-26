from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# MYSQL CONNECTION
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="adi@2400",
    database="ecopackai_db"
)

cursor = db.cursor()

materials = ["Recycled Paper", "Biodegradable Plastic", "Cardboard", "Mushroom Packaging"]

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/recommend", methods=["GET","POST"])
def recommend():

    result = None

    if request.method == "POST":

        weight = float(request.form["weight"])
        fragility = float(request.form["fragility"])
        priority = float(request.form["priority"])

        # ⭐ AI LOGIC (Direct Formula Model)
        co2 = (weight * 2.5) + (fragility * 1.2)
        cost = (weight * 4.0) + (fragility * 2.0)

        score = (co2 * priority) + cost
        best_material = materials[int(score) % 4]

        # SAVE DATABASE
        cursor.execute(
            "INSERT INTO history(weight,fragility,material,co2,cost) VALUES(%s,%s,%s,%s,%s)",
            (weight, fragility, best_material, co2, cost)
        )
        db.commit()

        result = {
            "material": best_material,
            "co2": round(co2,2),
            "cost": round(cost,2)
        }

    return render_template("recommend.html", result=result)


@app.route("/history")
def history():

    cursor.execute("SELECT * FROM history")
    data = cursor.fetchall()

    return render_template("history.html", data=data)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
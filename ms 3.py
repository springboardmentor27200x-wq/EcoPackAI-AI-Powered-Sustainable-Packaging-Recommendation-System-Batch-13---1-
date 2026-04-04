app.py (Flask Backend)
from flask import Flask, request, jsonify
app = Flask(name)
@app.route("/predict", methods=["POST"]) def predict_material(): data = request.json material_type = le.transform([data["material_type"]])[0]

input_data = [[
    material_type,
    data["strength"],
    data["weight_capacity"],
    data["biodegradability"],
    data["recyclability"]
]]

predicted_cost = model.predict(input_data)[0]

return jsonify({
    "predicted_cost": round(float(predicted_cost), 2),
    "recommendation": "Eco-friendly material recommended"
})

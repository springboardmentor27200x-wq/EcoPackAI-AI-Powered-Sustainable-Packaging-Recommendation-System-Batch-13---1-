from flask import Flask, request, jsonify, render_template
app = Flask(__name__, template_folder="templates")
@app.route('/')
def home():
    return render_template("index.html")
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    weight = data['weight']
    strength = data['strength']
    if weight < 5:
        material = "Paper"
        eco_score = 90
        co2 = 10 
    elif weight < 10:
        material = "Bioplastic"
        eco_score = 80
        co2 = 20
    else:
        material = "Metal"
        eco_score = 60
        co2 = 40
    return jsonify({
        "recommended_material": material,
        "eco_score": eco_score,
        "co2_emission": co2
    })
if __name__ == '__main__':
    app.run(debug=True)
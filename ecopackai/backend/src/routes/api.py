from flask import Blueprint, request, jsonify
from services.recommendation import get_recommendations, compute_environmental_score

api_bp = Blueprint('api', __name__)

@api_bp.route('/recommendations', methods=['POST'])
def recommendations():
    data = request.json
    product_input = data.get('product_input')
    
    if not product_input:
        return jsonify({'error': 'Product input is required'}), 400
    
    recommendations = get_recommendations(product_input)
    return jsonify(recommendations), 200

@api_bp.route('/environmental_score', methods=['POST'])
def environmental_score():
    data = request.json
    packaging_material = data.get('packaging_material')
    
    if not packaging_material:
        return jsonify({'error': 'Packaging material is required'}), 400
    
    score = compute_environmental_score(packaging_material)
    return jsonify({'environmental_score': score}), 200
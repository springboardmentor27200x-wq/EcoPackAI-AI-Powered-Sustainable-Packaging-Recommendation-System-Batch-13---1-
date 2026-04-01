from flask import jsonify
from models.database import get_db, engine
import psycopg2
import sys
import os

# Try to import from ml_model, if not available use mock
try:
    from ml_model.src.models.recommender import Recommender
except ImportError:
    # Create a mock Recommender class if ml_model is not available
    class Recommender:
        def __init__(self):
            pass
        
        def predict(self, product_data):
            # Mock prediction - returns sample recommendations
            return {
                "recommendations": [
                    {"material": "Recycled Paper", "score": 95},
                    {"material": "Biodegradable Plastic", "score": 85},
                    {"material": "Glass", "score": 90}
                ]
            }

class RecommendationService:
    def __init__(self):
        self.recommender = Recommender()

    def get_recommendations(self, product_data):
        # Validate input data
        if not self.validate_input(product_data):
            return jsonify({"error": "Invalid input data"}), 400
        
        # Generate recommendations using the AI model
        recommendations = self.recommender.predict(product_data)
        
        return jsonify(recommendations), 200

    def validate_input(self, product_data):
        # Implement validation logic for product_data
        required_fields = ['material_type', 'dimensions', 'weight']
        for field in required_fields:
            if field not in product_data:
                return False
        return True

    def save_recommendation_to_db(self, recommendation):
        """Save recommendation to database using SQLAlchemy"""
        try:
            # This is a placeholder - implement actual DB saving logic
            # Example: db.add(recommendation_object)
            #          db.commit()
            pass
        except Exception as e:
            print(f"Error saving to database: {e}")

    def compute_environmental_score(self, material):
        """Compute environmental score for a material"""
        # TODO: Implement scoring logic
        return {
            "material": material,
            "score": 85,  # Placeholder
            "description": "Environmental impact score"
        }


# Helper functions for API routes
def get_recommendations(product_input):
    """Get packaging recommendations for a product"""
    service = RecommendationService()
    try:
        recommendations = service.recommender.predict(product_input)
        return recommendations
    except Exception as e:
        return {"error": str(e)}


def compute_environmental_score(material):
    """Compute environmental score for a material"""
    service = RecommendationService()
    try:
        score = service.compute_environmental_score(material)
        return score
    except Exception as e:
        return {"error": str(e)}
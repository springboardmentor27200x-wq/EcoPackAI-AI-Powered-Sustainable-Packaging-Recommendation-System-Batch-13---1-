import joblib

model = joblib.load("cost_model.pkl")

print("Cost model features:", model.n_features_in_)
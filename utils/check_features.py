import joblib

scaler = joblib.load("scaler.pkl")

print("Number of features:", scaler.n_features_in_)

try:
    print("Feature names:", scaler.feature_names_in_)
except:
    print("Feature names not stored")
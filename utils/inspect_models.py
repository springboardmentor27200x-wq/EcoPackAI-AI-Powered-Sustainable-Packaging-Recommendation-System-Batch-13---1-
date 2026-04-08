import joblib

cost_model = joblib.load("cost_model.pkl")
co2_model = joblib.load("co2_model.pkl")
scaler = joblib.load("scaler.pkl")

print("---- COST MODEL ----")
print("Features:", cost_model.n_features_in_)

print("\n---- CO2 MODEL ----")
print("Features:", co2_model.n_features_in_)

print("\n---- SCALER ----")
print("Features:", scaler.n_features_in_)

try:
    print("Feature Names:", scaler.feature_names_in_)
except:
    print("Feature names not stored")
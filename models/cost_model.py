import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# create random training data
X = np.random.rand(200,4)

y_cost = np.random.rand(200)*100
y_co2 = np.random.rand(200)*50

# train models
cost_model = RandomForestRegressor()
co2_model = RandomForestRegressor()

cost_model.fit(X,y_cost)
co2_model.fit(X,y_co2)

# create models folder
os.makedirs("models", exist_ok=True)

# save models
joblib.dump(cost_model,"models/cost_model.pkl")
joblib.dump(co2_model,"models/co2_model.pkl")

print("Models created successfully!")
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
data = pd.read_csv("data.csv")

# Show data
print(data)

# CO2 Reduction
initial = data['CO2_Emission'][0]
latest = data['CO2_Emission'].iloc[-1]
reduction = ((initial - latest) / initial) * 100
print("CO2 Reduction %:", reduction)

# Cost Savings
initial_cost = data['Cost'][0]
latest_cost = data['Cost'].iloc[-1]
savings = initial_cost - latest_cost
print("Cost Savings:", savings)

# Plot graph
plt.plot(data['Month'], data['Material_Used'])
plt.title("Material Usage Trend")
plt.show()
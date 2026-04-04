import pandas as pd
import plotly.express as px

# Step 1: Load data
data = pd.read_csv("data.csv")

# Step 2: Display data
print("\nDataset:\n")
print(data)

# Step 3: Calculate CO2 Reduction %
co2_reduction = ((data['CO2_Emission'].iloc[0] - data['CO2_Emission'].iloc[-1]) 
                 / data['CO2_Emission'].iloc[0]) * 100

# Step 4: Calculate Cost Savings
cost_savings = data['Cost'].iloc[0] - data['Cost'].iloc[-1]

print("\nCO2 Reduction %:", co2_reduction)
print("Cost Savings:", cost_savings)

# Step 5: Create Graph (Material Usage Trend)
fig = px.line(
    data,
    x='Month',
    y='Material_Used',
    title='Material Usage Trend',
    markers=True
)

fig.show()

# Step 6: Save to Excel
data['CO2_Reduction_%'] = co2_reduction
data['Cost_Savings'] = cost_savings

data.to_excel("Sustainability_Report.xlsx", index=False)

print("\n✅ Report saved as Sustainability_Report.xlsx")
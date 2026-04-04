dashboard_report.py
import matplotlib.pyplot as plt

CO2 chart

plt.figure(figsize=(8, 5)) plt.bar(df["material_type"], df["co2_emission"]) plt.title("CO2 Emission by Material") plt.xticks(rotation=45) plt.tight_layout() plt.savefig("co2_chart.png") plt.show()

Cost trend

plt.figure(figsize=(8, 5)) plt.plot(df["material_type"], df["cost"], marker="o") plt.title("Cost Trend") plt.xticks(rotation=45) plt.tight_layout() plt.savefig("cost_chart.png") plt.show()

Excel report

df.to_excel("sustainability_report.xlsx", index=False) print("Report exported successfully")

if name == "main":

app.run(debug=True)
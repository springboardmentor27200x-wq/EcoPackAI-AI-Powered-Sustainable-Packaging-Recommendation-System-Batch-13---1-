import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="localhost",
    database="Ecopack",
    user="postgres",
    password="1234"
)

cur = conn.cursor()
df = pd.read_csv(r"C:\Users\jyots\OneDrive\Documents\Ecopackai\ecopack_backend\datasets\materials_1200_structured.csv")

# ensure only required columns
df = df[[
    "material_id",
    "material_name",
    "density_g_cm3",
    "strength_score",
    "weight_capacity_kg",
    "biodegradability_score",
    "recyclability_percent",
    "manufacturing_energy_index",
    "fragility_support",
    "moisture_resistance",
    "cost_target",
    "co2_target"
]]

cur.execute("DROP TABLE IF EXISTS materials")

cur.execute("""
CREATE TABLE materials (
material_id INT,
material_name TEXT,
density_g_cm3 FLOAT,
strength_score FLOAT,
weight_capacity_kg FLOAT,
biodegradability_score FLOAT,
recyclability_percent FLOAT,
manufacturing_energy_index FLOAT,
fragility_support INT,
moisture_resistance INT,
cost_target FLOAT,
co2_target FLOAT
)
""")

for row in df.itertuples(index=False):
    cur.execute("""
    INSERT INTO materials VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, row)

conn.commit()

print("✅ Materials Imported Successfully")
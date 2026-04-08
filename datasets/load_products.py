import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="localhost",
    database="Ecopack",
    user="postgres",
    password="1234"
)

cur = conn.cursor()

df = pd.read_csv("datasets/products_1000_structured.csv")

# encode categorical
df["fragility_level"] = df["fragility_level"].map({
    "Low": 1,
    "Medium": 2,
    "High": 3
})

df["moisture_sensitivity"] = df["moisture_sensitivity"].map({
    "Low": 1,
    "Medium": 2,
    "High": 3
})

cur.execute("DROP TABLE IF EXISTS products")

cur.execute("""
CREATE TABLE products (
product_id INT,
product_name TEXT,
product_category TEXT,
product_weight_kg FLOAT,
fragility_level INT,
moisture_sensitivity INT
)
""")

for row in df.itertuples(index=False):
    cur.execute("""
    INSERT INTO products VALUES (%s,%s,%s,%s,%s,%s)
    """, row)

conn.commit()

print("✅ Products Imported Successfully")
import os
import math
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FEATURES_PATH = os.path.join(BASE_DIR, 'feature_names.pkl')
COST_MODEL_PATH = os.path.join(BASE_DIR, 'cost_model.pkl')
CO2_MODEL_PATH = os.path.join(BASE_DIR, 'co2_model.pkl')

PRODUCTS_CSV = r'D:\infosysis internship\cleaned_product_dataset.csv'
MATERIALS_CSV = r'D:\infosysis internship\cleaned_material_dataset.csv'

FRAGILITY_MAP = {'low': 2.0, 'medium': 5.0, 'high': 9.0}
STRENGTH_MAP = {'low': 3.0, 'medium': 6.0, 'high': 9.0}
CATEGORY_SHIPPING_MAP = {
    'electronics': 1.10,
    'food': 1.20,
    'cosmetics': 1.05,
    'home appliances': 1.10,
    'toys': 1.00
}
FEATURE_COLUMNS = [
    'product_weight',
    'fragility_score',
    'required_strength_score',
    'shipping_score',
    'material_strength',
    'weight_capacity',
    'biodegradability_score',
    'co2_emission_score',
    'cost_per_unit',
    'recyclability_percent',
    'suitability_score'
]


def sample_products(products_df):
    sampled = []
    for _, group in products_df.groupby('category'):
        sampled.append(group.sample(n=min(len(group), 180), random_state=42))
    return pd.concat(sampled, ignore_index=True)


def sample_materials(materials_df):
    sampled = []
    for _, group in materials_df.groupby('material_type'):
        top_group = group.sort_values('suitability_score', ascending=False).head(500)
        sampled.append(top_group.sample(n=min(len(top_group), 180), random_state=42))
    return pd.concat(sampled, ignore_index=True)


def prepare_products(products_df):
    products = products_df.rename(columns={
        'product_category': 'category',
        'product_weight_kg': 'product_weight'
    }).copy()
    products['fragility_score'] = products['fragility_level'].str.strip().str.lower().map(FRAGILITY_MAP).fillna(5.0)
    products['required_strength_score'] = products['required_strength'].str.strip().str.lower().map(STRENGTH_MAP).fillna(6.0)
    products['shipping_score'] = products['category'].str.strip().str.lower().map(CATEGORY_SHIPPING_MAP).fillna(1.0)
    products['min_strength'] = products['required_strength'].str.strip().str.lower().map({'low': 1, 'medium': 5, 'high': 8}).fillna(5)
    products['max_strength'] = products['required_strength'].str.strip().str.lower().map({'low': 4, 'medium': 7, 'high': 10}).fillna(7)
    return products


def prepare_materials(materials_df):
    materials = materials_df.rename(columns={
        'material': 'material_name',
        'strength': 'material_strength',
        'biodegradability': 'biodegradability_score',
        'co2_score': 'co2_emission_score',
        'cost': 'cost_per_unit',
        'recyclability': 'recyclability_percent'
    }).copy()

    materials['material_type'] = materials['material_name'].apply(infer_material_type)
    materials['suitability_score'] = (
        materials['material_strength'] * 0.35 +
        materials['biodegradability_score'] * 0.30 +
        (materials['recyclability_percent'] / 10.0) * 0.20 +
        (11.0 - materials['co2_emission_score']) * 0.15
    ).round(4)
    return materials


def infer_material_type(name):
    lowered = str(name).strip().lower()
    if any(term in lowered for term in ['carton', 'paper', 'pulp', 'cardboard']):
        return 'Paper'
    if any(term in lowered for term in ['plastic', 'pla', 'foam']):
        return 'Bioplastic'
    if any(term in lowered for term in ['glass', 'metal']):
        return 'Eco-Friendly Composite'
    return 'Biodegradable'


def build_training_frame(products_df, materials_df):
    products_df['join_key'] = 1
    materials_df['join_key'] = 1
    training_df = products_df.merge(materials_df, on='join_key', how='inner').drop(columns=['join_key'])

    training_df = training_df[
        (training_df['weight_capacity'] >= training_df['product_weight']) &
        (training_df['material_strength'] >= training_df['min_strength']) &
        (training_df['material_strength'] <= training_df['max_strength'])
    ].copy()

    training_df['fragility_factor'] = 1.0 + (training_df['fragility_score'] / 20.0)
    training_df['shipping_factor'] = training_df['shipping_score']
    training_df['eco_factor'] = (
        1.3 - (training_df['biodegradability_score'] / 20.0) - (training_df['recyclability_percent'] / 250.0)
    ).clip(lower=0.25)
    training_df['strength_bonus'] = (
        1.05 - (training_df['material_strength'] - training_df['required_strength_score']).abs() / 20.0
    ).clip(lower=0.85)

    training_df['target_cost'] = (
        training_df['product_weight'] * training_df['cost_per_unit'] * training_df['shipping_factor'] * training_df['fragility_factor'] / training_df['strength_bonus']
    )
    training_df['target_co2'] = (
        training_df['product_weight'] * training_df['co2_emission_score'] * training_df['shipping_factor'] * training_df['eco_factor'] / (training_df['suitability_score'] / 4.0).clip(lower=0.8)
    )

    return training_df[FEATURE_COLUMNS + ['target_cost', 'target_co2']]


def main():
    products_raw = pd.read_csv(PRODUCTS_CSV)
    materials_raw = pd.read_csv(MATERIALS_CSV)

    products_df = prepare_products(products_raw)
    materials_df = prepare_materials(materials_raw)

    sampled_products = sample_products(products_df)
    sampled_materials = sample_materials(materials_df)
    training_df = build_training_frame(sampled_products, sampled_materials)
    if training_df.empty:
        raise RuntimeError('No training rows were produced from the CSV datasets.')

    X = training_df[FEATURE_COLUMNS]
    y_cost = training_df['target_cost']
    y_co2 = training_df['target_co2']

    X_train, X_test, y_cost_train, y_cost_test, y_co2_train, y_co2_test = train_test_split(
        X, y_cost, y_co2, test_size=0.2, random_state=42
    )

    cost_model = RandomForestRegressor(n_estimators=40, max_depth=12, min_samples_leaf=4, random_state=42, n_jobs=-1)
    co2_model = RandomForestRegressor(n_estimators=40, max_depth=12, min_samples_leaf=4, random_state=42, n_jobs=-1)

    cost_model.fit(X_train, y_cost_train)
    co2_model.fit(X_train, y_co2_train)

    cost_pred = cost_model.predict(X_test)
    co2_pred = co2_model.predict(X_test)

    print('products_rows=', len(products_raw))
    print('materials_rows=', len(materials_raw))
    print('sampled_products=', len(sampled_products))
    print('sampled_materials=', len(sampled_materials))
    print('training_rows=', len(training_df))
    print('cost_mae=', round(mean_absolute_error(y_cost_test, cost_pred), 4))
    print('cost_rmse=', round(math.sqrt(mean_squared_error(y_cost_test, cost_pred)), 4))
    print('cost_r2=', round(r2_score(y_cost_test, cost_pred), 4))
    print('co2_mae=', round(mean_absolute_error(y_co2_test, co2_pred), 4))
    print('co2_rmse=', round(math.sqrt(mean_squared_error(y_co2_test, co2_pred)), 4))
    print('co2_r2=', round(r2_score(y_co2_test, co2_pred), 4))

    joblib.dump(cost_model, COST_MODEL_PATH)
    joblib.dump(co2_model, CO2_MODEL_PATH)
    joblib.dump(FEATURE_COLUMNS, FEATURES_PATH)
    print('Saved models to', BASE_DIR)


if __name__ == '__main__':
    main()



import os
import pandas as pd
import numpy as np
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, mean_squared_error, mean_absolute_error, roc_auc_score
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "industrial_iot_timeseries.csv")
# Models are written straight into the backend, which loads them at runtime
MODELS_DIR = os.path.join(BASE_DIR, "..", "backend", "app", "ml_models")
REPORTS_DIR = os.path.join(BASE_DIR, "outputs", "reports")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

print("🚀 Starting Phase 2: Predictive Maintenance ML Training")
print("-" * 60)

# 1. Load Data
print("Loading dataset...")
df = pd.read_csv(DATA_FILE, parse_dates=['timestamp'])
print(f"Dataset shape: {df.shape}")

# Create derived features mentioned in EDA
# We sort by machine and time first
df = df.sort_values(by=['machine_id', 'timestamp']).reset_index(drop=True)

# Add rolling features and derivatives for both machines
print("Applying feature engineering (rolling windows, derivatives)...")
engineered_dfs = []
for machine_id, group in df.groupby('machine_id'):
    # Derivatives (rates of change)
    if 'osmoseur' in group['machine_type'].iloc[0]:
        group['pression_rate'] = group['pression_membrane_bar'].diff().fillna(0)
        group['conductivite_rate'] = group['conductivite_permeat_uscm'].diff().fillna(0)
        # Drop columns not relevant for osmoseur to keep clean inputs
        machine_cols = ['debit_permeat_lh', 'debit_concentrat_lh', 'conductivite_permeat_uscm', 
                        'ph_entree', 'ph_sortie', 'turbidite_ntu', 'chlore_libre_mgl', 
                        'durete_totale_f', 'tds_ppm', 'pression_membrane_bar', 'temperature_eau_c',
                        'pression_rate', 'conductivite_rate']
    else:
        group['vibrations_rate'] = group['vibrations_moteur_mms'].diff().fillna(0)
        group['mtbf_rate'] = group['mtbf_h'].diff().fillna(0)
        machine_cols = ['temperature_remplissage_c', 'volume_remplissage_l', 'carbonation_co_gl', 
                        'unites_produites', 'heures_arret_h', 'mtbf_h', 'conso_air_co_m3h', 'vibrations_moteur_mms',
                        'vibrations_rate', 'mtbf_rate']
    
    # Simple rolling means (1h = 12 steps)
    for col in machine_cols:
        group[f'{col}_rolling_1h'] = group[col].rolling(12, min_periods=1).mean()
        
    engineered_dfs.append(group)

df = pd.concat(engineered_dfs).sort_index()

# Extract Data by Machine
osmoseur_df = df[df['machine_type'] == 'osmoseur'].copy()
remplisseuse_df = df[df['machine_type'] == 'remplisseuse'].copy()

# Feature lists
FEATURES_OSM = [
    'debit_permeat_lh', 'debit_concentrat_lh', 'conductivite_permeat_uscm', 
    'ph_entree', 'ph_sortie', 'turbidite_ntu', 'chlore_libre_mgl', 
    'durete_totale_f', 'tds_ppm', 'pression_membrane_bar', 'temperature_eau_c',
    'pression_rate', 'conductivite_rate'
] + [f'{c}_rolling_1h' for c in ['debit_permeat_lh', 'debit_concentrat_lh', 'conductivite_permeat_uscm', 'ph_entree', 'ph_sortie', 'turbidite_ntu', 'chlore_libre_mgl', 'durete_totale_f', 'tds_ppm', 'pression_membrane_bar', 'temperature_eau_c', 'pression_rate', 'conductivite_rate']]

FEATURES_RMP = [
    'temperature_remplissage_c', 'volume_remplissage_l', 'carbonation_co_gl', 
    'unites_produites', 'heures_arret_h', 'mtbf_h', 'conso_air_co_m3h', 'vibrations_moteur_mms',
    'vibrations_rate', 'mtbf_rate'
] + [f'{c}_rolling_1h' for c in ['temperature_remplissage_c', 'volume_remplissage_l', 'carbonation_co_gl', 'unites_produites', 'heures_arret_h', 'mtbf_h', 'conso_air_co_m3h', 'vibrations_moteur_mms', 'vibrations_rate', 'mtbf_rate']]

metrics_report = {}

def evaluate_classification(y_test, y_pred, y_prob=None, model_name=""):
    print(f"\n--- Evaluation for {model_name} ---")
    rep = classification_report(y_test, y_pred, output_dict=True)
    print(classification_report(y_test, y_pred))
    
    if y_prob is not None:
        try:
            auc = roc_auc_score(y_test, y_prob)
            print(f"ROC AUC Score: {auc:.4f}")
            rep['roc_auc'] = auc
        except:
            pass
    metrics_report[model_name] = rep

def evaluate_regression(y_test, y_pred, model_name=""):
    print(f"\n--- Evaluation for {model_name} ---")
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    metrics_report[model_name] = {"RMSE": rmse, "MAE": mae}

# ==============================================================================
# Model 1: Isolation Forest (Anomaly Detection)
# ==============================================================================
print("\n[1] Training Isolation Forest for Anomaly Detection (Unsupervised)...")
# We train separate models per machine due to distinct sensor distributions
for m_name, m_df, m_features in [("osmoseur", osmoseur_df, FEATURES_OSM), ("remplisseuse", remplisseuse_df, FEATURES_RMP)]:
    print(f"  -> {m_name.capitalize()}")
    scaler = StandardScaler()
    X = scaler.fit_transform(m_df[m_features])
    
    # Contamination roughly set to 5% based on overall incident rate
    iso_forest = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
    iso_forest.fit(X)
    
    # Save the scaler and model
    joblib.dump(scaler, f"{MODELS_DIR}/iso_forest_scaler_{m_name}.joblib")
    joblib.dump(iso_forest, f"{MODELS_DIR}/iso_forest_{m_name}.joblib")

print("Done. Models saved.")

# ==============================================================================
# Model 2: XGBoost (Failure Prediction - failure_within_24h)
# ==============================================================================
print("\n[2] Training XGBoost for 24h Failure Prediction...")
for m_name, m_df, m_features in [("osmoseur", osmoseur_df, FEATURES_OSM), ("remplisseuse", remplisseuse_df, FEATURES_RMP)]:
    print(f"  -> {m_name.capitalize()}")
    X = m_df[m_features]
    y = m_df['failure_within_24h']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Handle Class Imbalance with SMOTE
    print("     Applying SMOTE...")
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    
    xgb = XGBClassifier(
        n_estimators=200, 
        max_depth=5, 
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )
    
    xgb.fit(X_train_res, y_train_res)
    
    y_pred = xgb.predict(X_test)
    y_prob = xgb.predict_proba(X_test)[:, 1]
    
    evaluate_classification(y_test, y_pred, y_prob, model_name=f"XGBoost_Failure24h_{m_name}")
    joblib.dump(xgb, f"{MODELS_DIR}/xgboost_failure24h_{m_name}.joblib")

# ==============================================================================
# Model 3: Random Forest & Logistic Regression (Production Quality Prediction)
# ==============================================================================
# Typically applied primarily to the Remplisseuse since it dictates bottle quality
print("\n[3] Training Production Quality Prediction (Remplisseuse only)...")
# Target: Quality Risk score threshold -> Binary classification (risk > 0.1)
y_qual = (remplisseuse_df['quality_risk_score'] > 0.1).astype(int)
X_qual = remplisseuse_df[FEATURES_RMP]

X_train_q, X_test_q, y_train_q, y_test_q = train_test_split(X_qual, y_qual, test_size=0.2, random_state=42, stratify=y_qual)

# Logistic Regression (Baseline/Interpretable)
scaler_lr = StandardScaler()
X_train_q_scaled = scaler_lr.fit_transform(X_train_q)
X_test_q_scaled = scaler_lr.transform(X_test_q)

lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train_q_scaled, y_train_q)
y_pred_lr = lr.predict(X_test_q_scaled)
evaluate_classification(y_test_q, y_pred_lr, lr.predict_proba(X_test_q_scaled)[:, 1], model_name="LogisticRegression_QualityRMP")

joblib.dump(scaler_lr, f"{MODELS_DIR}/lr_quality_scaler.joblib")
joblib.dump(lr, f"{MODELS_DIR}/lr_quality_model.joblib")

# Random Forest
rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X_train_q, y_train_q)
y_pred_rf = rf.predict(X_test_q)
evaluate_classification(y_test_q, y_pred_rf, rf.predict_proba(X_test_q)[:, 1], model_name="RandomForest_QualityRMP")

joblib.dump(rf, f"{MODELS_DIR}/rf_quality_model.joblib")

# ==============================================================================
# Model 4: Gradient Boosting Regressor (RUL / Health Index)
# ==============================================================================
print("\n[4] Training Gradient Boosting Regressor for RUL (Health Index proxy)...")
for m_name, m_df, m_features in [("osmoseur", osmoseur_df, FEATURES_OSM), ("remplisseuse", remplisseuse_df, FEATURES_RMP)]:
    print(f"  -> {m_name.capitalize()}")
    X = m_df[m_features]
    y = m_df['health_index']  # We use health index as a proxy for RUL continuous prediction
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    gbr = GradientBoostingRegressor(n_estimators=150, max_depth=5, learning_rate=0.1, random_state=42)
    gbr.fit(X_train, y_train)
    
    y_pred = gbr.predict(X_test)
    evaluate_regression(y_test, y_pred, model_name=f"GBR_HealthIndex_{m_name}")
    
    joblib.dump(gbr, f"{MODELS_DIR}/gbr_health_{m_name}.joblib")

# ==============================================================================
# Save Metrics Report
# ==============================================================================
with open(f"{REPORTS_DIR}/ml_metrics.json", "w") as f:
    json.dump(metrics_report, f, indent=4)

print("\n🎯 All models trained successfully. Saved to `backend/app/ml_models/`.")
print("📊 Performance metrics saved to `outputs/reports/ml_metrics.json`.")

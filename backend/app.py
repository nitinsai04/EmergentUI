from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import numpy as np
import pandas as pd
import xgboost as xgb
from tensorflow.keras.models import load_model
from dotenv import load_dotenv
from pathlib import Path
from typing import List

# Original Imports
from simulation import DigitalTwinSimulation
from simulation_config import SimulationParams, SimulationResult

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI()

# ==========================================
# ML MODEL LOADING (Singleton) 
# ==========================================
def find_model_path():
    # Start looking from the current file's directory
    current = Path(__file__).resolve().parent
    
    # Search upwards for the 'ml_pipeline' folder (max 3 levels up)
    for _ in range(3):
        target = current / "ml_pipeline" / "models"
        if target.exists():
            return target
        current = current.parent
    return None

MODEL_DIR = find_model_path()

if MODEL_DIR is None:
    # Fallback to the absolute path found in your terminal logs
    MODEL_DIR = Path(r"E:\finalproj\EmergentUI\ml_pipeline\models")

XGB_PATH = MODEL_DIR / "xgboost_attack_classifier.json"
LSTM_PATH = MODEL_DIR / "lstm_rul_model.h5"

print(f"--- DEBUG INFO ---")
print(f"Searching for models in: {MODEL_DIR}")
print(f"XGB File exists: {XGB_PATH.exists()}")
print(f"LSTM File exists: {LSTM_PATH.exists()}")
print(f"------------------")

if not XGB_PATH.exists():
    raise FileNotFoundError(f"CRITICAL: Cannot find {XGB_PATH.name} in {MODEL_DIR}.")

print("--- Initializing AI Models ---")
clf = xgb.XGBClassifier()
clf.load_model(str(XGB_PATH))
# compile=False is used to avoid Keras 3 version mismatch errors
rul_model = load_model(str(LSTM_PATH), compile=False)
print("--- AI Models Loaded Successfully ---")

ATTACK_LABELS = ["Normal", "Mechanical Fault", "Sensor Spoofing", "Packet Dropout", "Freezing Sensor"]

# ==========================================
# CORS CONFIGURATION
# ==========================================
origins = ["http://localhost:3000", "http://localhost:8000", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# HELPER: FEATURE EXTRACTION
# ==========================================
def extract_live_features(results_dict):
    df = pd.DataFrame(results_dict)
    sensor_val = df["omega_sensor"].ffill().fillna(0)
    residual = np.abs(df["omega_true"] - sensor_val)
    
    window_size = 50
    feature_list = []
    
    for i in range(len(df)):
        if i < window_size:
            # ADDED A 7th ZERO to match the model's expectation
            feature_list.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, sensor_val.iloc[i]])
        else:
            win_res = residual.iloc[i-window_size:i]
            win_sens = sensor_val.iloc[i-window_size:i]
            
            # We add one more derived feature (e.g., raw residual) 
            # to bring the count to 7
            features = [
                float(win_res.mean()),
                float(win_res.std()),
                float(win_res.max()),
                float(np.polyfit(range(window_size), win_res, 1)[0]),
                float(np.sum(win_res ** 2)),
                float(win_sens.mean()),
                float(residual.iloc[i]) # <--- This is likely the 7th feature
            ]
            feature_list.append(features)
            
    return np.array(feature_list)

# ==========================================
# ROUTES
# ==========================================

@app.get("/api/")
def read_root():
    return {"message": "Digital Twin Simulation API Ready"}

@app.post("/api/simulate")
def run_simulation(params: SimulationParams):
    try:
        # FIX: Pydantic V2 uses model_dump() instead of dict()
        sim = DigitalTwinSimulation(params.model_dump())
        results = sim.run() 
        
        # 1. Extract features from physics output
        features = extract_live_features(results)
        
        # 2. XGBoost Attack Classification
        attack_indices = clf.predict(features)
        results["ai_attack_label"] = attack_indices.tolist()
        results["ai_status_text"] = [ATTACK_LABELS[int(i)] for i in attack_indices]
        
        # 3. LSTM Remaining Useful Life (RUL) Prediction
        lookback = 10
        lstm_inputs = []
        for i in range(len(features)):
            if i < lookback:
                # Provide a zero-padded window for the start of simulation
                lstm_inputs.append(np.zeros((lookback, 6)))
            else:
                lstm_inputs.append(features[i-lookback:i])
        
        lstm_inputs = np.array(lstm_inputs)
        # verbose=0 keeps the terminal clean during live requests
        predictions = rul_model.predict(lstm_inputs, verbose=0)
        results["ai_predicted_rul"] = predictions.flatten().tolist()
        
        return results

    except Exception as e:
        print(f"Simulation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-dataset")
def generate_dataset(count: int = 100):
    datasets = []
    for i in range(min(count, 10)):
        p = {"Kt": 0.1 + np.random.normal(0, 0.01), "voltage": 12.0 + np.random.normal(0, 1.0), "duration": 5.0, "dt": 0.1}
        sim = DigitalTwinSimulation(p)
        res = sim.run()
        datasets.append(res)
    return {"message": f"Generated {count} samples", "preview": datasets}

if __name__ == "__main__":
    import uvicorn
    # Port 8001 must match your Frontend's BACKEND_URL
    uvicorn.run(app, host="0.0.0.0", port=8001)
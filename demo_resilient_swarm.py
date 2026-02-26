"""
Unified Resilient Swarm Demo: Coupled Motors + Dual AI Models
Demonstrates motor cooperation, cyber-resilience, and high variability.
"""
import sys
import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import joblib
from pathlib import Path
from tensorflow.keras.models import load_model

import time
import random

# FORCE ENTRPY: Ensure every run is truly unique
seed = int((time.time() * 1000000) % 2**32)
np.random.seed(seed)
random.seed(seed)

# Path Configuration
ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
sys.path.append(str(BACKEND_DIR))
sys.path.append(str(ROOT / "ml_pipeline"))

from simulation import CoupledMotorSimulation
from kalman_filter import MotorKalmanFilter
from utils.feature_extractor import extract_features_from_window, calculate_fusion_residual

# Model Loading
MODEL_DIR = ROOT / "ml_pipeline" / "models"
XGB_PATH = MODEL_DIR / "xgboost_attack_classifier.json"
LSTM_PATH = MODEL_DIR / "lstm_rul_model.keras"
SCALER_PATH = MODEL_DIR / "lstm_scaler.joblib"

print(f"[SYSTEM] Entropy Seed Initialized: {seed}")
print("[LOADING] AI Models...")
clf = xgb.XGBClassifier()
clf.load_model(str(XGB_PATH))
rul_model = load_model(str(LSTM_PATH), compile=False)
scaler = joblib.load(str(SCALER_PATH)) if SCALER_PATH.exists() else None

ATTACK_LABELS = ["Normal", "Mechanical Fault", "Sensor Spoofing", "Packet Dropout", "Freezing Sensor"]

def run_resilient_swarm_demo():
    # SCENARIO ENGINE: Re-evaluate everything on every call
    scenarios = [
        {"name": "Aggressive Spoofing", "attack": "Sensor Spoofing", "mag": np.random.uniform(5.5, 9.0), "fault": "Friction Buildup", "f_mag": 0.05},
        {"name": "Stealthy Spoofing", "attack": "Sensor Spoofing", "mag": np.random.uniform(-4.0, -2.0), "fault": "None", "f_mag": 0.0},
        {"name": "Communication Loss", "attack": "Packet Dropout", "mag": 0.0, "fault": "Bearing Fault", "f_mag": 0.0},
        {"name": "Sensor Freeze", "attack": "Freezing Sensor", "mag": 0.0, "fault": "Friction Buildup", "f_mag": 0.08},
        {"name": "Intermittent Spoof", "attack": "Sensor Spoofing", "mag": np.random.uniform(3.0, 5.0), "fault": "None", "f_mag": 0.0}
    ]
    
    scene = random.choice(scenarios)
    attack_start = np.random.uniform(2.5, 5.5)
    fault_start = np.random.uniform(0.5, 2.5)
    noise_lvl = np.random.uniform(0.05, 0.2)
    
    print(f"\n[SCENARIO] '{scene['name']}' selected.")
    print(f"           Attack: {scene['attack']} at {attack_start:.2f}s")
    print(f"           Fault: {scene['fault']} at {fault_start:.2f}s")
    print(f"           Process Noise: {noise_lvl:.3f}")

    params = {
        "duration": 8.0, 
        "attack_type": scene["attack"],
        "attack_start_time": attack_start,
        "attack_magnitude": scene["mag"],
        "fault_type": scene["fault"],
        "fault_start_time": fault_start,
        "noise_level": noise_lvl,
        "target_speed": np.random.uniform(10.0, 14.0)
    }
    
    sim = CoupledMotorSimulation(params)
    kf_a = MotorKalmanFilter()
    
    history = []
    buffer_a = []
    feature_buffer = []
    LOOKBACK = 15
    
    # Run Simulation
    for t in np.arange(0, 8.0, 0.02):
        state = sim.step(t)
        
        # Monitor Motor A (The Target)
        z_speed_a = state["motor_a_sensor"]
        z_curr_a = state["motor_a_current"]
        z_temp_a = state["motor_a_temp"]
        voltage_a = state["motor_a_voltage"]
        
        # Kalman for Motor A
        est_a, innov_a = kf_a.filter(voltage_a, z_speed_a if not np.isnan(z_speed_a) else 0.0)
        
        # Features for Motor A
        curr_res_a = calculate_fusion_residual(voltage_a, z_speed_a if not np.isnan(z_speed_a) else 0.0, z_curr_a)
        res_speed_a = np.abs(z_speed_a - est_a) if not np.isnan(z_speed_a) else 5.0 # Large residual for dropout
        
        buffer_a.append({"res": res_speed_a, "innov": innov_a, "curr_res": curr_res_a, "kalman": est_a, "temp": z_temp_a})
        
        attack_label = "Normal"
        attack_prob = 0.0
        predicted_rul = 100.0
        
        if len(buffer_a) >= 50:
            win = pd.DataFrame(buffer_a[-50:])
            feats = extract_features_from_window(win)
            feats["temp_mean"] = win["temp"].mean()
            feats["temp_slope"] = np.polyfit(range(len(win)), win["temp"], 1)[0]
            
            # 1. XGBoost Detection
            pred = clf.predict(feats)[0]
            attack_label = ATTACK_LABELS[int(pred)]
            attack_prob = np.max(clf.predict_proba(feats)[0]) * 100
            
            # 2. LSTM Health
            feature_vector = [
                feats["innov_mean"].values[0], feats["innov_std"].values[0], feats["innov_kurtosis"].values[0],
                feats["fusion_res_mean"].values[0], feats["fusion_res_std"].values[0],
                feats["temp_mean"].values[0], feats["temp_slope"].values[0]
            ]
            feature_buffer.append(feature_vector)
            
            if len(feature_buffer) >= LOOKBACK:
                if pred not in [2, 3, 4]: # Clean signal
                    seq = np.array(feature_buffer[-LOOKBACK:])
                    inp = (scaler.transform(seq) if scaler else seq).reshape(1, LOOKBACK, -1)
                    rul_raw = rul_model.predict(inp, verbose=0)
                    current_rul = min(100.0, max(0.0, float(rul_raw[0][0]) * 12.5))
                    
                    if history:
                        prev_rul = history[-1]["predicted_rul"]
                        predicted_rul = min(prev_rul, current_rul) # Monotonic
                    else:
                        predicted_rul = current_rul
                else:
                    predicted_rul = history[-1]["predicted_rul"] if history else 100.0
                
                if len(feature_buffer) > 100: feature_buffer.pop(0)
            buffer_a.pop(0)

        history.append({
            "time": t,
            "omega_load": state["omega_load"],
            "motor_a_sensor": z_speed_a,
            "motor_b_voltage": state["motor_b_voltage"],
            "attack_label": attack_label,
            "attack_prob": attack_prob,
            "predicted_rul": predicted_rul
        })
        
    return pd.DataFrame(history), scene

def visualize_swarm(df, scene):
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
    plt.subplots_adjust(hspace=0.35)
    
    # 1. Motor Speed & Cooperation
    ax1 = axes[0]
    ax1.plot(df['time'], df['omega_load'], 'g', label='Shared Load Speed', linewidth=2.5)
    ax1.plot(df['time'], df['motor_a_sensor'], 'r:', label='Motor A Sensor (Target)', alpha=0.5)
    ax1.set_title(f"Resilient Swarm: Cooperative Maintenance (Scenario: {scene['attack']})", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Speed (rad/s)")
    ax1.legend()
    ax1.grid(True, alpha=0.2)
    
    # 2. Motor B Compensation (Voltage)
    ax2 = axes[1]
    ax2.plot(df['time'], df['motor_b_voltage'], 'blue', label='Motor B Voltage (Cooperative Neighbor)', linewidth=2)
    ax2.fill_between(df['time'], 12, df['motor_b_voltage'], where=(df['motor_b_voltage'] > 12.5), color='blue', alpha=0.1)
    ax2.set_title("Swarm Cooperation: Neighbor Compensating for Fault/Attack", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Voltage (V)")
    ax2.legend()
    ax2.grid(True, alpha=0.2)
    
    # 3. XGBoost Security Monitor
    ax3 = axes[2]
    colors = {"Normal": "green", "Mechanical Fault": "orange", "Sensor Spoofing": "red", "Packet Dropout": "purple", "Freezing Sensor": "brown"}
    for label in df['attack_label'].unique():
        mask = df['attack_label'] == label
        ax3.scatter(df[mask]['time'], df[mask]['attack_prob'], c=colors.get(label, 'gray'), label=label, s=8)
    ax3.set_title("XGBoost Security Monitor (Motor A)", fontsize=12, fontweight='bold')
    ax3.set_ylabel("Confidence (%)")
    ax3.legend(loc='lower left', fontsize='small')
    ax3.grid(True, alpha=0.2)
    
    # 4. LSTM Health Index
    ax4 = axes[3]
    valid_df = df[df['predicted_rul'] < 100]
    if not valid_df.empty:
        ax4.plot(valid_df['time'], valid_df['predicted_rul'], 'b', linewidth=2, label='RUL Health %')
        ax4.fill_between(valid_df['time'], valid_df['predicted_rul'], color='blue', alpha=0.1)
    ax4.set_title("LSTM Life Index: Physical Asset Health", fontsize=12, fontweight='bold')
    ax4.set_ylabel("Health %")
    ax4.set_xlabel("Time (s)")
    ax4.set_ylim(0, 110)
    ax4.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("--- ULTIMATE RESILIENT SWARM DEMO ---")
    data, scene = run_resilient_swarm_demo()
    visualize_swarm(data, scene)

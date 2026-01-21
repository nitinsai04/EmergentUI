import sys
import os
import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import kurtosis, skew

# ==========================================
# 1. PATH CONFIGURATION (Must be BEFORE imports)
# ==========================================
ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
sys.path.append(str(BACKEND_DIR))

# Now we can safely import from backend
try:
    from simulation import DigitalTwinSimulation
    from kalman_filter import MotorKalmanFilter
    from adaptive_engine import MotorParameterEstimator
    print("✅ Backend modules loaded successfully.")
except ImportError as e:
    print(f"❌ Error: Could not find backend modules. Looking in: {BACKEND_DIR}")
    print(f"Details: {e}")
    sys.exit(1)

# ==========================================
# 2. MODEL LOADING
# ==========================================
MODEL_PATH = ROOT / "ml_pipeline" / "models" / "xgboost_attack_classifier.json"
if not MODEL_PATH.exists():
    print(f"❌ Error: Model file not found at {MODEL_PATH}")
    sys.exit(1)

clf = xgb.XGBClassifier()
clf.load_model(str(MODEL_PATH))

def run_active_defense_simulation():
    # Setup simulation with a spoofing attack at 4.0 seconds
    sim = DigitalTwinSimulation({
        "duration": 8.0, 
        "attack_type": "Sensor Spoofing", 
        "attack_start_time": 4.0,
        "attack_magnitude": 5.0  # Visual deviation
    })
    
    kf = MotorKalmanFilter()
    adaptive = MotorParameterEstimator()
    
    history, buffer = [], []
    omega_prev, b_est = 0.0, 0.01
    dt = 0.02

    print("🚀 Simulation started. Running for 8 seconds...")

    for t in np.arange(0, 8.0, dt):
        # In your simulation.py, use run() or a step method. 
        # For this demo, we simulate the state:
        raw_states = sim.run() # This returns a dict of lists
        # We find the index for current time
        idx = int(t / dt)
        if idx >= len(raw_states["time"]): break
            
        z = raw_states["omega_sensor"][idx]
        actual = raw_states["omega_true"][idx]
        voltage = 12.0
        
        # 1. Kalman Update with current estimated friction
        kf.update_parameters(b=b_est)
        est, innov = kf.filter(voltage, z)
        
        # 2. Synchronized Feature Extraction
        res = np.abs(z - est)
        buffer.append({"res": res, "innov": innov, "kalman": est})
        
        final_speed, attack_active = z, False
        
        if len(buffer) >= 50:
            win = pd.DataFrame(buffer[-50:])
            # Calculate Features for XGBoost
            feats = pd.DataFrame([{
                "res_mean": win["res"].mean(),
                "res_std": win["res"].std(),
                "innov_mean": win["innov"].mean(),
                "innov_std": win["innov"].std(),
                "innov_max": np.max(np.abs(win["innov"])),
                "innov_kurtosis": kurtosis(win["innov"]),
                "innov_skew": skew(win["innov"]),
                "innov_crest": np.max(np.abs(win["innov"])) / (np.sqrt(np.mean(win["innov"]**2)) + 1e-6),
                "res_slope": np.polyfit(range(50), win["res"], 1)[0],
                "omega_kalman_mean": win["kalman"].mean()
            }])
            
            # Predict
            pred = clf.predict(feats)[0]
            
            if pred in [2, 3, 4]: # Attack detected (Spoofing, Dropout, Freeze)
                attack_active = True
                final_speed = est # <--- OVERRIDE: Use Digital Twin estimate
            else:
                # Only update friction model when data is trusted
                b_est, _ = adaptive.update(voltage, z, omega_prev, dt)
            
            buffer.pop(0)

        history.append({
            "time": t, 
            "actual": actual, 
            "sensor": z, 
            "defended": final_speed, 
            "attack": attack_active
        })
        omega_prev = final_speed

    return pd.DataFrame(history)

# ==========================================
# 3. EXECUTION & PLOTTING
# ==========================================
if __name__ == "__main__":
    df = run_active_defense_simulation()

    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['actual'], 'k--', label='True Speed (Ground Truth)', alpha=0.8)
    plt.plot(df['time'], df['sensor'], 'r', label='Sensor Speed (Hacked)', alpha=0.4)
    plt.plot(df['time'], df['defended'], 'g', label='Defended Speed (Digital Twin)', linewidth=2)
    
    # Highlight attack region
    attack_times = df[df['attack'] == True]['time']
    if not attack_times.empty:
        plt.axvspan(attack_times.min(), attack_times.max(), color='red', alpha=0.1, label='Attack Detected')

    plt.title("Resilient Digital Twin: Real-Time Cyber-Attack Mitigation")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Motor Speed (rad/s)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    print("📊 Plot generated. Showing results...")
    plt.show()
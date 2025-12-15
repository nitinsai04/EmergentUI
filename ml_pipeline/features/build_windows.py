import pandas as pd
import numpy as np

# =====================
# CONFIG
# =====================
DATA_PATH = "data/all_simulations.csv"
OUTPUT_PATH = "data/window_features.csv"


WINDOW_SIZE = 50     # timesteps per window
STRIDE = 10          # overlap

# =====================
# LOAD DATA
# =====================
df = pd.read_csv(DATA_PATH)

feature_rows = []

# =====================
# PROCESS PER RUN
# =====================
for run_id, run_df in df.groupby("run_id"):
    run_df = run_df.sort_values("time").reset_index(drop=True)

    for start in range(0, len(run_df) - WINDOW_SIZE, STRIDE):
        window = run_df.iloc[start:start + WINDOW_SIZE]

        # -----------------
        # Residual signal
        # -----------------
        residual = np.abs(window["omega_true"] - window["omega_sensor"])

        # -----------------
        # Features
        # -----------------
        features = {
            "res_mean": residual.mean(),
            "res_std": residual.std(),
            "res_max": residual.max(),
            "res_min": residual.min(),
            "res_range": residual.max() - residual.min(),
            "res_slope": np.polyfit(range(len(residual)), residual, 1)[0],
            "res_energy": np.sum(residual ** 2),

            # Optional dynamics
            "omega_sensor_mean": window["omega_sensor"].mean(),
            "omega_sensor_std": window["omega_sensor"].std(),
        }

        # -----------------
        # Labels (window-level)
        # -----------------
        fault_active = window["fault_active"].max()
        attack_active = window["attack_active"].max()

        if attack_active == 1:
            label = 2      # Attack
        elif fault_active == 1:
            label = 1      # Fault
        else:
            label = 0      # Normal

        features["label"] = label
        features["run_id"] = run_id

        feature_rows.append(features)

# =====================
# SAVE OUTPUT
# =====================
features_df = pd.DataFrame(feature_rows)
features_df.to_csv(OUTPUT_PATH, index=False)

print(f"Windowed dataset saved to {OUTPUT_PATH}")
print(features_df["label"].value_counts())

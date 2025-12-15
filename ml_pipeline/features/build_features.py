import pandas as pd
import numpy as np
from utils.config import WINDOW_SIZE, STRIDE, DATA_PATH

def extract_features(df):
    rows = []

    for start in range(0, len(df) - WINDOW_SIZE, STRIDE):
        window = df.iloc[start:start + WINDOW_SIZE]

        residual = np.abs(window["omega_true"] - window["omega_sensor"])

        features = {
            "res_mean": residual.mean(),
            "res_std": residual.std(),
            "res_max": residual.max(),
            "res_min": residual.min(),
            "res_slope": np.polyfit(range(len(residual)), residual, 1)[0],

            # labels (use majority vote)
            "fault": window["fault_active"].max(),
            "attack": window["attack_active"].max()
        }

        rows.append(features)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    features_df = extract_features(df)
    features_df.to_csv("../data/features.csv", index=False)
    print("Feature extraction complete.")

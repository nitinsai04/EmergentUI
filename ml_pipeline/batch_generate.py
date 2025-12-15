import requests
import pandas as pd

API = "http://localhost:8001/api/simulate"

ALL_ROWS = []

N_RUNS = 60

for run_id in range(N_RUNS):
    scenario = run_id % 4

    params = {
        "duration": 5.0,
        "dt": 0.02,

        # defaults
        "fault_type": "None",
        "fault_severity": 0.4,
        "fault_start_time": 1.5,

        "attack_type": "None",
        "attack_magnitude": 1.5,
        "attack_start_time": 3.0,
    }

    # Scenario assignment
    if scenario == 1:
        params["fault_type"] = "Torque Drop"
    elif scenario == 2:
        params["attack_type"] = "Sensor Spoofing"
    elif scenario == 3:
        params["fault_type"] = "Torque Drop"
        params["attack_type"] = "Sensor Spoofing"

    res = requests.post(API, json=params)
    res.raise_for_status()

    df = pd.DataFrame(res.json())
    df["run_id"] = run_id   # 🔑 important
    ALL_ROWS.append(df)

final_df = pd.concat(ALL_ROWS, ignore_index=True)
final_df.to_csv("data/all_simulations.csv", index=False)

print(f"Generated {N_RUNS} simulations → data/all_simulations.csv")

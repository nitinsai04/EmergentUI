"""
Cooperative Motor Demo: Shared Load Compensation
This script demonstrates two motors working together to maintain a shared load.
If one motor is attacked or fails, the other increases its voltage/torque to compensate.
"""
import sys
import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
from pathlib import Path

# Path Configuration
ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
sys.path.append(str(BACKEND_DIR))

from simulation import CoupledMotorSimulation

def run_cooperative_demo():
    # Randomize parameters for variability
    attack_start = np.random.uniform(3.0, 4.5)
    attack_mag = np.random.uniform(4.0, 7.0)
    
    print(f"[CONFIG] Random Attack Start: {attack_start:.2f}s, Magnitude: {attack_mag:.2f}")

    params = {
        "duration": 8.0, 
        "attack_type": "Sensor Spoofing",
        "attack_start_time": attack_start,
        "attack_magnitude": attack_mag,
        "target_speed": 12.0
    }
    
    sim = CoupledMotorSimulation(params)
    history = sim.run()
    
    return pd.DataFrame(history)

def visualize_cooperation(df):
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: Speeds
    ax1 = axes[0]
    ax1.plot(df['time'], [12.0]*len(df), 'k--', label='Target Speed', alpha=0.5)
    ax1.plot(df['time'], df['omega_load'], 'g', label='Shared Load Speed', linewidth=3)
    ax1.plot(df['time'], df['motor_a_sensor'], 'r:', label='Motor A Sensor (Hacked)', alpha=0.6)
    ax1.plot(df['time'], df['motor_b_sensor'], 'b:', label='Motor B Sensor (Healthy)', alpha=0.6)
    
    ax1.set_title("Cooperative Load Sharing: Speed Maintenance", fontsize=14, fontweight='bold')
    ax1.set_ylabel("Speed (rad/s)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Voltages (Compensation effort)
    ax2 = axes[1]
    ax2.plot(df['time'], df['motor_a_voltage'], 'r', label='Motor A Voltage', alpha=0.7)
    ax2.plot(df['time'], df['motor_b_voltage'], 'b', label='Motor B Voltage (Compensating)', linewidth=2)
    
    ax2.set_title("Control Effort: Motor B Compensating for System Stress", fontsize=14, fontweight='bold')
    ax2.set_ylabel("Voltage (V)")
    ax2.set_xlabel("Time (seconds)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Highlight compensation area
    # Find where Motor B voltage significantly increases above base (12V)
    comp_mask = (df['motor_b_voltage'] > 13.0)
    if comp_mask.any():
        ax2.fill_between(df['time'], 12, df['motor_b_voltage'], where=comp_mask, color='blue', alpha=0.2, label='Cooperation Active')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("--- Starting Cooperative Multi-Motor Simulation ---")
    df = run_cooperative_demo()
    visualize_cooperation(df)

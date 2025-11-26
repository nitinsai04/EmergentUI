import numpy as np
from typing import List, Dict, Optional
import random

class DigitalTwinSimulation:
    def __init__(self, params: Dict):
        self.Kt = params.get("Kt", 0.1)
        self.J = params.get("J", 10.0)
        self.b = params.get("b", 0.01)
        self.load_torque = params.get("load_torque", 0.5)
        self.voltage = params.get("voltage", 12.0)
        self.dt = params.get("dt", 0.01)
        self.duration = params.get("duration", 10.0)
        self.noise_level = params.get("noise_level", 0.0)
        
        # Fault Config
        self.fault_type = params.get("fault_type", "None")
        self.fault_severity = params.get("fault_severity", 0.0)
        self.fault_start_time = params.get("fault_start_time", 0.0)
        
        # Attack Config
        self.attack_type = params.get("attack_type", "None")
        self.attack_magnitude = params.get("attack_magnitude", 0.0)
        self.attack_start_time = params.get("attack_start_time", 0.0)

    def run(self) -> Dict[str, List[float]]:
        steps = int(self.duration / self.dt)
        time = np.linspace(0, self.duration, steps)
        
        omega = 0.0
        omega_history = []
        torque_history = []
        load_history = []
        sensor_history = []
        
        last_valid_sensor = 0.0
        
        for t in time:
            # 1. Apply Faults (Physical Parameter Changes)
            current_b = self.b
            current_Kt = self.Kt
            current_load = self.load_torque
            
            if t >= self.fault_start_time:
                if self.fault_type == "Bearing Friction":
                    current_b *= (1 + self.fault_severity)
                elif self.fault_type == "Torque Drop":
                    current_Kt *= (1 - self.fault_severity)
                elif self.fault_type == "Sudden Load Spike":
                    # Spike lasts for 10% of duration or 1s
                    if t < self.fault_start_time + 1.0:
                        current_load *= (1 + self.fault_severity)

            # 2. Physics Step (Euler Integration)
            # dω/dt = (Kt * V – loadTorque – b * ω) / J
            motor_torque = current_Kt * self.voltage
            friction_torque = current_b * omega
            net_torque = motor_torque - current_load - friction_torque
            
            alpha = net_torque / self.J
            omega += alpha * self.dt
            
            # 3. Sensor Simulation (Measurement)
            # Add Gaussian Noise
            noise = np.random.normal(0, self.noise_level) if self.noise_level > 0 else 0
            omega_measured = omega + noise
            
            # 4. Apply Cyber Attacks (Data Corruption)
            if t >= self.attack_start_time:
                if self.attack_type == "Sensor Spoofing":
                    omega_measured += self.attack_magnitude
                elif self.attack_type == "Freezing Sensor":
                    omega_measured = last_valid_sensor # Keep previous value
                elif self.attack_type == "Packet Dropout":
                    # Randomly drop packets based on magnitude (probability)
                    if random.random() < self.attack_magnitude:
                        omega_measured = None # Represent as None or NaN
            
            # Update last valid for freezing logic
            if omega_measured is not None:
                last_valid_sensor = omega_measured
            else:
                # For plotting, we might want to hold last value or show gap
                # Here we'll just use last valid to keep graph continuous but flat, 
                # or we could use a specific error code. Let's use last_valid for continuity
                # but in a real system it would be missing.
                # For visualization, let's actually store None to let frontend handle gaps if possible,
                # or just repeat last valid to simulate 'hold'
                omega_measured = last_valid_sensor 

            omega_history.append(omega)
            torque_history.append(motor_torque)
            load_history.append(current_load)
            sensor_history.append(omega_measured)

        return {
            "time": time.tolist(),
            "omega_true": omega_history,
            "omega_sensor": sensor_history,
            "torque": torque_history,
            "load": load_history
        }

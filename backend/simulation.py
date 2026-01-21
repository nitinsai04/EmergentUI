import numpy as np
from typing import List, Dict
import random

class DigitalTwinSimulation:
    def __init__(self, params: Dict):
        # Existing Motor Params
        self.Kt = params.get("Kt", 0.1)     # Torque constant
        self.Ke = params.get("Ke", 0.1)     # Back-EMF constant
        self.R = params.get("R", 2.0)       # Terminal Resistance (Ohms)
        self.J = params.get("J", 10.0)      # Inertia
        self.b = params.get("b", 0.01)      # Friction
        
        # Environmental Params
        self.T_ambient = params.get("T_ambient", 25.0) # Room temp
        self.thermal_mass = params.get("thermal_mass", 50.0) 
        
        self.load_torque = params.get("load_torque", 0.5)
        self.voltage = params.get("voltage", 12.0)
        self.dt = params.get("dt", 0.01)
        self.duration = params.get("duration", 10.0)
        self.noise_level = params.get("noise_level", 0.05)

        # Fault & Attack Config
        self.fault_type = params.get("fault_type", "None")
        self.fault_severity = params.get("fault_severity", 0.0)
        self.fault_start_time = params.get("fault_start_time", 0.0)
        self.attack_type = params.get("attack_type", "None")
        self.attack_magnitude = params.get("attack_magnitude", 0.0)
        self.attack_start_time = params.get("attack_start_time", 0.0)

    def run(self) -> Dict[str, List]:
        steps = int(self.duration / self.dt)
        time = np.linspace(0, self.duration, steps)

        # Initial States
        omega = 0.0
        temp = self.T_ambient
        last_valid_speed = 0.0

        # Logs
        omega_true, omega_sensor = [], []
        current_true, current_sensor = [], []
        temp_true, temp_sensor = [], []
        
        attack_active_hist = []
        fault_active_hist = []

        for t in time:
            # 1. Check Faults
            fault_active = 1 if (t >= self.fault_start_time and self.fault_type != "None") else 0
            current_b = self.b * (1 + self.fault_severity) if (fault_active and self.fault_type == "Bearing Friction") else self.b
            
            # 2. PHYSICS ENGINE (Multi-Modal)
            # A. Electrical: I = (V - Ke*omega) / R
            # The current depends on speed (Back-EMF effect)
            current = (self.voltage - self.Ke * omega) / self.R
            
            # B. Mechanical: J*d_omega/dt = Kt*I - load - b*omega
            motor_torque = self.Kt * current
            net_torque = motor_torque - self.load_torque - current_b * omega
            omega += (net_torque / self.J) * self.dt
            
            # C. Thermal: dT/dt = (I^2 * R - cooling) / mass
            # Joule heating creates temperature rise
            heat_generated = (current**2) * self.R
            cooling = (temp - self.T_ambient) * 0.1 # Simple convective cooling
            temp += ((heat_generated - cooling) / self.thermal_mass) * self.dt

            # 3. SENSOR LAYER (Add Gaussian Noise to all 3)
            def add_noise(val): return val + np.random.normal(0, self.noise_level)
            
            m_speed = add_noise(omega)
            m_current = add_noise(current)
            m_temp = add_noise(temp)

            # 4. ATTACK LAYER (Only Speed Sensor is usually hacked)
            attack_active = 1 if (t >= self.attack_start_time and self.attack_type != "None") else 0
            if attack_active:
                if self.attack_type == "Sensor Spoofing":
                    m_speed += self.attack_magnitude
                elif self.attack_type == "Freezing Sensor":
                    m_speed = last_valid_speed
            
            last_valid_speed = m_speed

            # 5. STORE
            omega_true.append(omega); omega_sensor.append(m_speed)
            current_true.append(current); current_sensor.append(m_current)
            temp_true.append(temp); temp_sensor.append(m_temp)
            attack_active_hist.append(attack_active)
            fault_active_hist.append(fault_active)

        return {
            "time": time.tolist(),
            "omega_true": omega_true, "omega_sensor": omega_sensor,
            "current_true": current_true, "current_sensor": current_sensor,
            "temp_true": temp_true, "temp_sensor": temp_sensor,
            "attack_active": attack_active_hist,
            "fault_active": fault_active_hist
        }
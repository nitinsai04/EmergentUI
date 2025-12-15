import numpy as np
from typing import List, Dict
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

        # Fault config
        self.fault_type = params.get("fault_type", "None")
        self.fault_severity = params.get("fault_severity", 0.0)
        self.fault_start_time = params.get("fault_start_time", 0.0)

        # Attack config
        self.attack_type = params.get("attack_type", "None")
        self.attack_magnitude = params.get("attack_magnitude", 0.0)
        self.attack_start_time = params.get("attack_start_time", 0.0)

    def run(self) -> Dict[str, List]:
        steps = int(self.duration / self.dt)
        time = np.linspace(0, self.duration, steps)

        omega = 0.0
        last_valid_sensor = 0.0

        omega_true = []
        omega_sensor = []
        torque_hist = []
        load_hist = []

        attack_type_hist = []
        attack_active_hist = []
        fault_type_hist = []
        fault_active_hist = []

        for t in time:
            # ---------------- Fault flags ----------------
            fault_active = 0
            if t >= self.fault_start_time and self.fault_type != "None":
                fault_active = 1

            # ---------------- Apply faults ----------------
            current_b = self.b
            current_Kt = self.Kt
            current_load = self.load_torque

            if fault_active:
                if self.fault_type == "Bearing Friction":
                    current_b *= (1 + self.fault_severity)
                elif self.fault_type == "Torque Drop":
                    current_Kt *= (1 - self.fault_severity)
                elif self.fault_type == "Sudden Load Spike":
                    if t < self.fault_start_time + 1.0:
                        current_load *= (1 + self.fault_severity)

            # ---------------- Physics ----------------
            motor_torque = current_Kt * self.voltage
            net_torque = motor_torque - current_load - current_b * omega
            omega += (net_torque / self.J) * self.dt

            # ---------------- Sensor ----------------
            noise = np.random.normal(0, self.noise_level) if self.noise_level > 0 else 0
            measured = omega + noise

            # ---------------- Attack flags ----------------
            attack_active = 0
            if t >= self.attack_start_time and self.attack_type != "None":
                attack_active = 1

                if self.attack_type == "Sensor Spoofing":
                    measured += self.attack_magnitude
                elif self.attack_type == "Freezing Sensor":
                    measured = last_valid_sensor
                elif self.attack_type == "Packet Dropout":
                    if random.random() < self.attack_magnitude:
                        measured = None

            # Handle missing sensor values
            if measured is not None:
                last_valid_sensor = measured
            else:
                measured = last_valid_sensor

            # ---------------- Store everything ----------------
            omega_true.append(omega)
            omega_sensor.append(measured)
            torque_hist.append(motor_torque)
            load_hist.append(current_load)

            attack_type_hist.append(self.attack_type)
            attack_active_hist.append(attack_active)
            fault_type_hist.append(self.fault_type)
            fault_active_hist.append(fault_active)

        return {
            "time": time.tolist(),
            "omega_true": omega_true,
            "omega_sensor": omega_sensor,
            "torque": torque_hist,
            "load": load_hist,
            "attack_type": attack_type_hist,
            "attack_active": attack_active_hist,
            "fault_type": fault_type_hist,
            "fault_active": fault_active_hist
        }

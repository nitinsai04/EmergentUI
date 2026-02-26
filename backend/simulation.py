import numpy as np

class DigitalTwinSimulation:
    def __init__(self, params):
        self.dt = params.get("dt", 0.02)
        self.duration = params.get("duration", 5.0)
        
        # Physics Parameters
        self.J = 0.01  # Inertia
        self.b = 0.1   # Friction
        self.K = 0.1   # Torque Constant (Should match Ke approx)
        self.R = 2.0   # Resistance (Ohms) - NEW
        self.Ke = 0.1  # Back-EMF Constant - NEW
        
        # State Variables
        # State Variables
        self.omega_true = 0.0
        self.voltage = 12.0
        self.temp = 25.0 # Ambient Temp (deg C)
        
        # Attack/Fault Parameters
        self.attack_type = params.get("attack_type", "None")
        self.attack_start = params.get("attack_start_time", 2.0)
        self.mag = params.get("attack_magnitude", 0.0)
        
        # Physical Fault Parameters
        self.fault_type = params.get("fault_type", "None")
        self.fault_start = params.get("fault_start_time", 1.0)
        self.noise_level = params.get("noise_level", 0.1) # Default 0.1

    def step(self, t):
        # 1. Calculate True Physics (Mechanical)
        # Torque = J*alpha + b*omega => alpha = (K*V - b*omega)/J
        alpha = (self.K * self.voltage - self.b * self.omega_true) / self.J
        self.omega_true += alpha * self.dt

        # 2. Calculate True Physics (Electrical) - NEW
        # Ohm's Law: V = I*R + Ke*omega => I = (V - Ke*omega) / R
        true_current = (self.voltage - self.Ke * self.omega_true) / self.R
        
        # 2a. Inject Physical Faults
        if t >= self.fault_start:
            if self.fault_type == "Friction Buildup":
                # Linear increase in friction - Aggressive for Demo
                self.b += 0.05 * self.dt  # 10x faster degradation
            elif self.fault_type == "Bearing Fault":
                self.omega_true += np.sin(t * 50) * 0.5

        # 2b. Simulate Temperature Rise
        power_loss = self.b * (self.omega_true ** 2)
        k_heat, k_cool = 20.0, 0.1 # 10x more heat, less cooling
        d_temp = (power_loss * k_heat - (self.temp - 25.0) * k_cool) * self.dt
        self.temp += d_temp

        # 3. Generate Sensor Data with Noise
        sensor_speed = self.omega_true + np.random.normal(0, self.noise_level)
        sensor_current = true_current + np.random.normal(0, 0.02)
        sensor_temp = self.temp + np.random.normal(0, 0.5)

        # 4. Apply Cyber Attacks
        if t >= self.attack_start:
            if self.attack_type == "Sensor Spoofing":
                sensor_speed += self.mag
            elif self.attack_type == "Freezing Sensor":
                # Concept: sensor stops updating (logic handled in run loop usually)
                pass 
            elif self.attack_type == "Packet Dropout":
                sensor_speed = np.nan

        return {
            "time": t,
            "omega_true": self.omega_true,
            "omega_sensor": sensor_speed,
            "current_true": true_current,     # NEW
            "current_sensor": sensor_current, # NEW
            "voltage": self.voltage,
            "temp_sensor": sensor_temp        # NEW for RUL
        }

    def run(self):
        data = []
        for t in np.arange(0, self.duration, self.dt):
            data.append(self.step(t))
        return data

class CoupledMotorSimulation:
    def __init__(self, params):
        self.dt = params.get("dt", 0.02)
        self.duration = params.get("duration", 8.0)
        
        # Shared Load Parameters
        self.target_load_speed = params.get("target_speed", 12.0)
        self.load_inertia = 0.05
        self.load_friction = 0.2
        self.omega_load = 0.0
        
        # Two Motors
        self.motor_a = DigitalTwinSimulation({**params, "duration": self.duration, "dt": self.dt})
        self.motor_b = DigitalTwinSimulation({**params, "duration": self.duration, "dt": self.dt, "attack_type": "None", "fault_type": "None"})
        
        # Control Gains
        self.kp = 1.5
        
    def step(self, t):
        # 1. Determine Control Action for each motor
        # In a coupled system, motors try to maintain the load speed
        err_a = self.target_load_speed - self.omega_load
        err_b = self.target_load_speed - self.omega_load
        
        # Motor B is "Cooperative" - it monitors the load speed and works harder if it drops
        # If Motor A is lagging (due to fault/attack), Motor B will see the speed drop and increase its torque
        
        self.motor_a.voltage = np.clip(12.0 + self.kp * err_a, 0, 24)
        self.motor_b.voltage = np.clip(12.0 + self.kp * err_b, 0, 24)
        
        # 2. Step individual motors (internal physics)
        res_a = self.motor_a.step(t)
        res_b = self.motor_b.step(t)
        
        # 3. Update Shared Load Physics
        # Total Torque = K_a*I_a + K_b*I_b - load_friction*omega_load
        total_torque = (self.motor_a.K * res_a["current_true"] + 
                        self.motor_b.K * res_b["current_true"])
        
        load_alpha = (total_torque - self.load_friction * self.omega_load) / self.load_inertia
        self.omega_load += load_alpha * self.dt
        
        # Override motor speeds with coupled load speed (assuming rigid coupling)
        # In a real system, there's some slip, but for this demo, they are locked.
        self.motor_a.omega_true = self.omega_load
        self.motor_b.omega_true = self.omega_load
        
        return {
            "time": t,
            "omega_load": self.omega_load,
            "motor_a_sensor": res_a["omega_sensor"],
            "motor_b_sensor": res_b["omega_sensor"],
            "motor_a_voltage": self.motor_a.voltage,
            "motor_b_voltage": self.motor_b.voltage,
            "motor_a_current": res_a["current_sensor"],
            "motor_b_current": res_b["current_sensor"],
            "motor_a_temp": res_a["temp_sensor"],
            "motor_b_temp": res_b["temp_sensor"]
        }

    def run(self):
        data = []
        for t in np.arange(0, self.duration, self.dt):
            data.append(self.step(t))
        return data

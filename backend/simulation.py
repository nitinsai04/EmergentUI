import numpy as np                                                      #numpy is the gold standard for scientific computing in Python. Standard Python is a bit slow at doing math on long lists of numbers; numpy is extremely fast.    
from typing import List, Dict                                           #These are used for Type Hinting. Python is a "flexible" language, meaning it usually doesn't care what you put in a variable. However, in big projects, this leads to bugs. Type Hinting is a way to tell both the computer and other programmers what type of data you expect (like List, Dict, float, int, etc.). This makes your code safer and easier to understand.
import random                                                           #While numpy also has random functions, the standard random library is often used for simple "Yes/No" or "Coin Flip" logic.

class DigitalTwinSimulation:
    def __init__(self, params: Dict):                                   # constructor # named as __init__ always    #self.Kt: This means "save this value inside this specific object so I can use it later in other functions (like run)."        #Inside the code, self allows the computer to know whether it is updating the Kt for sim1 or sim2. 
        self.Kt = params.get("Kt", 0.1)                                 # params.get("Kt", 0.1): This means "look inside the params dictionary for a key named 'Kt'. If you find it, use its value. If you don't find it, use 0.1 as the default value."  
        self.J = params.get("J", 10.0)                                         
        self.b = params.get("b", 0.01)
        self.load_torque = params.get("load_torque", 0.5)
        self.voltage = params.get("voltage", 12.0)
        self.dt = params.get("dt", 0.01)
        self.duration = params.get("duration", 10.0)
        self.noise_level = params.get("noise_level", 0.0)               #kt (Efficiency) of motor #J (Inertia) of rotor  #b (Friction/Damping) of motor #load_torque: External load on motor shaft #voltage: Voltage applied to motor #dt: Time step for simulation #duration: Total time to simulate #noise_level: Standard deviation of Gaussian noise added to sensor readings

        # Fault config
        self.fault_type = params.get("fault_type", "None")
        self.fault_severity = params.get("fault_severity", 0.0)
        self.fault_start_time = params.get("fault_start_time", 0.0)

        # Attack config
        self.attack_type = params.get("attack_type", "None")
        self.attack_magnitude = params.get("attack_magnitude", 0.0)
        self.attack_start_time = params.get("attack_start_time", 0.0)

    def run(self) -> Dict[str, List]:                                   #In Python, every method inside a class must take self as its first argument. This gives the run method permission to access the data we saved earlier in __init__.Because run has self, it can look up self.voltage or self.duration to do its math 
        steps = int(self.duration / self.dt)                            #steps: Total number of data points (e.g., if duration is 10s and dt is 0.01s, you get 1000 steps).    #how many "ticks" of the clock occur
        time = np.linspace(0, self.duration, steps)                     #time: A list created by numpy (np) that holds every timestamp from 0 to the end.         #The np.linspace(0, 10, 1000) function: This creates 1,000 perfectly spaced points between 0 and 10 seconds.

        omega = 0.0                                                     #This is the starting speed of the motor (at rest).
        last_valid_sensor = 0.0

        omega_true = []                                                 #Empty Lists ([]): Think of these as logs. For every second of the simulation, we will "record" the speed, torque, and status into these lists.
        omega_sensor = []
        torque_hist = []
        load_hist = []

        attack_type_hist = []
        attack_active_hist = []
        fault_type_hist = []
        fault_active_hist = []

        for t in time:                                                  #The code inside this loop runs hundreds or thousands of times (once for every timestamp t)
            # ---------------- Fault flags ----------------
            fault_active = 0                                            #at each timestep(iteration), we start by assuming no fault is active (fault_active = 0). Then, we check if the current time t has reached or passed the fault_start_time and if a fault type other than "None" is specified. If both conditions are met, we set fault_active to 1, indicating that a fault is now active in the simulation.
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
                    if t < self.fault_start_time + 1.0:                 #the if t < self.fault_start_time + 1.0 part makes this spike temporary (lasting only 1 second).    sudden dip in speed ($\omega$). Because the "Net Torque" (the leftover force) suddenly drops or goes negative, the motor slows down instantly until the spike passes.
                        current_load *= (1 + self.fault_severity)

            # ---------------- Physics ----------------
            motor_torque = current_Kt * self.voltage
            net_torque = motor_torque - current_load - current_b * omega
            omega += (net_torque / self.J) * self.dt                    #initially omega is 0.0, so in the first iteration, it increases based on the net torque calculated from the motor torque, load, and friction.

            # ---------------- Sensor ----------------
            noise = np.random.normal(0, self.noise_level) if self.noise_level > 0 else 0        #Normal Distribution (also called a Gaussian Distribution or a Bell Curve)
            measured = omega + noise

            # ---------------- Attack flags ----------------
            attack_active = 0                                           #Similar to fault_active, we start by assuming no attack is active (attack_active = 0). Then, we check if the current time t has reached or passed the attack_start_time and if an attack type other than "None" is specified. If both conditions are met, we set attack_active to 1, indicating that an attack is now active in the simulation.
            if t >= self.attack_start_time and self.attack_type != "None": #if yes get in this block else skip
                attack_active = 1

                if self.attack_type == "Sensor Spoofing":
                    measured += self.attack_magnitude
                elif self.attack_type == "Freezing Sensor":
                    measured = last_valid_sensor
                elif self.attack_type == "Packet Dropout":
                    if random.random() < self.attack_magnitude:         #random.random() picks a number between 0 and 1. If that number is less than attack_magnitude (which should be between 0 and 1), we simulate a packet dropout by setting
                        measured = None

            # Handle missing sensor values                              #If the measured value is not None (i.e., we have a valid sensor reading), we update last_valid_sensor to this new value. If measured is None (indicating a packet dropout), we set measured to last_valid_sensor, effectively "holding" the last known good value.    
            if measured is not None:
                last_valid_sensor = measured
            else:
                measured = last_valid_sensor

            # ---------------- Store everything ----------------
            omega_true.append(omega)                                    #At the end of every loop iteration, the code appends (adds) the current values to the history lists.
            omega_sensor.append(measured)
            torque_hist.append(motor_torque)
            load_hist.append(current_load)

            attack_type_hist.append(self.attack_type)
            attack_active_hist.append(attack_active)
            fault_type_hist.append(self.fault_type)
            fault_active_hist.append(fault_active)

        return {
            "time": time.tolist(),                                      #Convert numpy arrays to standard Python lists for JSON serialization.  
            "omega_true": omega_true,
            "omega_sensor": omega_sensor,
            "torque": torque_hist,
            "load": load_hist,
            "attack_type": attack_type_hist,
            "attack_active": attack_active_hist,
            "fault_type": fault_type_hist,
            "fault_active": fault_active_hist
        }


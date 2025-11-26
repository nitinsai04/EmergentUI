from pydantic import BaseModel
from typing import Optional, List

class SimulationParams(BaseModel):
    Kt: float = 0.1
    J: float = 10.0
    b: float = 0.01
    load_torque: float = 0.5
    voltage: float = 12.0
    dt: float = 0.01
    duration: float = 10.0
    noise_level: float = 0.01
    
    fault_type: str = "None"
    fault_severity: float = 0.0
    fault_start_time: float = 5.0
    
    attack_type: str = "None"
    attack_magnitude: float = 0.0
    attack_start_time: float = 5.0

class SimulationResult(BaseModel):
    time: List[float]
    omega_true: List[float]
    omega_sensor: List[float]
    torque: List[float]
    load: List[float]

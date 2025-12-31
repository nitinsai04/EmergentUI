import numpy as np

class MotorKalmanFilter:
    def __init__(self, dt=0.02, J=0.01, b=0.1, K=0.01):
        # Physical Constants
        self.dt = dt
        self.J = J
        self.b = b
        self.K = K

        # State Matrix (Transition)
        # Next_Speed = Current_Speed + (dt/J) * (-b * Current_Speed + K * Voltage)
        self.A = np.array([[1 - (b * dt / J)]])
        self.B = np.array([[K * dt / J]])
        self.H = np.array([[1.0]])  # Measurement Matrix

        # Covariance Matrices
        self.Q = np.array([[0.001]]) # Process Noise (how much we trust physics)
        self.R = np.array([[0.05]])  # Measurement Noise (how much we trust sensor)
        self.P = np.array([[1.0]])   # Estimate Error Covariance
        
        self.x = np.array([[0.0]])   # Initial State (Speed = 0)

    def filter(self, voltage, z_measured):
        """
        z_measured: The noisy omega_sensor value
        returns: (corrected_estimate, innovation)
        """
        # 1. Predict
        x_pred = self.A @ self.x + self.B * voltage
        self.P = self.A @ self.P @ self.A.T + self.Q

        # 2. Update (Correct)
        innovation = z_measured - (self.H @ x_pred)
        S = self.H @ self.P @ self.H.T + self.R
        K_gain = self.P @ self.H.T @ np.linalg.inv(S)

        self.x = x_pred + K_gain @ innovation
        self.P = (np.eye(1) - K_gain @ self.H) @ self.P

        return float(self.x[0][0]), float(innovation[0][0])
import numpy as np

class MotorParameterEstimator:
    def __init__(self, initial_b=0.1, initial_J=0.01):
        # We want to estimate theta = [b, J]
        self.theta = np.array([initial_b, initial_J])
        self.P = np.eye(2) * 100  # Covariance matrix (uncertainty)
        self.lambda_ = 0.999      # Forgetting factor (0.999 = remember long term)

    def update(self, v_input, omega_current, omega_prev, dt):
        """
        Uses RLS to update friction (b) and inertia (J)
        Physics: J * (d_omega/dt) + b * omega = K * V
        """
        # 1. Calculate the derivative (acceleration)
        alpha = (omega_current - omega_prev) / dt
        
        # 2. Regressor vector [omega, alpha]
        phi = np.array([[omega_current], [alpha]])
        
        # 3. Target (The force applied by voltage)
        # Assuming K (torque constant) is known/stable at 0.01
        K = 0.01
        y = K * v_input
        
        # 4. RLS Math: Error calculation
        error = y - (phi.T @ self.theta)
        
        # 5. Gain update
        K_gain = (self.P @ phi) / (self.lambda_ + phi.T @ self.P @ phi)
        
        # 6. Update parameters
        self.theta = self.theta + (K_gain.flatten() * error)
        
        # 7. Update uncertainty
        self.P = (self.P - (K_gain @ phi.T @ self.P)) / self.lambda_
        
        return self.theta[0], self.theta[1] # Returns [new_b, new_J]
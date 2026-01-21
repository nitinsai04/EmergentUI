import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
import os

# =====================
# CONFIG - UPDATED PATH
# =====================
# Point this to the processed window features
DATA_PATH = "ml_pipeline/data/window_features.csv"
MODEL_PATH = "ml_pipeline/models/lstm_rul_model.keras"
LOOKBACK = 15

# =====================
# DATA PREPARATION
# =====================
if not os.path.exists(DATA_PATH):
    print(f"Error: {DATA_PATH} not found. Run build_windows.py first.")
    exit()

df = pd.read_csv(DATA_PATH).dropna()

# IMPROVEMENT: Use the new Kalman and Advanced features
features = [
    "res_mean", "res_std", "innov_mean", "innov_std", 
    "innov_max", "innov_kurtosis", "res_slope"
]
X_raw = df[features].values
y_raw = df["RUL"].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)

def create_sequences(data, target, lookback):
    X_seq, y_seq = [], []
    for i in range(len(data) - lookback):
        X_seq.append(data[i : i + lookback])
        y_seq.append(target[i + lookback])
    return np.array(X_seq), np.array(y_seq)

X, y = create_sequences(X_scaled, y_raw, LOOKBACK)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# =====================
# BUILD ENHANCED LSTM
# =====================
model = Sequential([
    LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True),
    BatchNormalization(), # IMPROVEMENT: Stability
    Dropout(0.2),
    
    LSTM(32, return_sequences=False),
    Dropout(0.2),
    
    Dense(16, activation='relu'),
    Dense(1, activation='linear') 
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# =====================
# TRAIN
# =====================
stop = EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True)

history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=32,
    callbacks=[stop],
    verbose=1
)

# =====================
# RUL COMPARISON OUTPUT
# =====================
# This section makes the results easy to understand
predictions = model.predict(X_test)

print("\n" + "="*40)
print("RUL PREDICTION CHECK (Actual vs Predicted)")
print("="*40)
comparison_df = pd.DataFrame({
    "Actual RUL (s)": y_test.flatten(),
    "Predicted RUL (s)": predictions.flatten(),
    "Error (s)": np.abs(y_test.flatten() - predictions.flatten())
})

# Print the first 10 results to see correctness
print(comparison_df.head(10).to_string(index=False))
print("="*40)

# =====================
# SAVE & PLOT
# =====================
model.save(MODEL_PATH)
plt.plot(history.history['mae'], label='Train MAE')
plt.plot(history.history['val_mae'], label='Val MAE')
plt.title('RUL Prediction Accuracy (MAE)')
plt.ylabel('Seconds Error')
plt.xlabel('Epoch')
plt.legend()
plt.show()
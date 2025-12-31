import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.impute import SimpleImputer # Added for data integrity
from imblearn.over_sampling import SMOTE 
import seaborn as sns
import matplotlib.pyplot as plt
import os

# =====================
# CONFIG
# =====================
DATA_PATH = "data/window_features.csv"
MODEL_SAVE_PATH = "models/xgboost_attack_classifier.json"

if not os.path.exists("models"):
    os.makedirs("models")

# =====================
# LOAD DATA
# =====================
if not os.path.exists(DATA_PATH):
    print(f"Error: {DATA_PATH} not found. Run build_windows.py first.")
    exit()

df = pd.read_csv(DATA_PATH)

# Separating features and labels
X = df.drop(columns=["label", "run_id", "RUL"])
y = df["label"]

# FIX: Use Imputation instead of dropna()
# This prevents the deletion of entire classes (Normal/Fault) 
# that may contain NaN values in complex statistical features.
imputer = SimpleImputer(strategy='mean')
X_clean = imputer.fit_transform(X)
X_clean = pd.DataFrame(X_clean, columns=X.columns)

# =====================
# BALANCING DATASET (SMOTE)
# =====================
# Creates synthetic samples for minority classes to prevent majority bias
print(f"Original label distribution: {dict(y.value_counts())}")
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_clean, y)
print(f"Resampled label distribution: {dict(y_resampled.value_counts())}")

# =====================
# TRAIN / TEST SPLIT
# =====================
# Stratify ensures the test set maintains the balanced class proportions
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.25, random_state=42, stratify=y_resampled
)

# =====================
# MULTI-CLASS MODEL
# =====================
print("Training Multi-Class XGBoost Model with enhanced depth and regularization...")

# Using deeper trees to capture non-linear relationships in Kurtosis/Skewness
model = xgb.XGBClassifier(
    objective="multi:softprob",
    num_class=5,
    n_estimators=300,        
    max_depth=8,             
    learning_rate=0.05,      
    subsample=0.8,           
    colsample_bytree=0.8,    
    eval_metric="mlogloss",
    random_state=42
)

model.fit(X_train, y_train)

# =====================
# EVALUATION
# =====================
y_pred = model.predict(X_test)
target_names = ["Normal", "Fault", "Spoofing", "Dropout", "Freeze"]

print("\n" + "="*30)
print("CLASSIFICATION REPORT")
print("="*30)
print(classification_report(y_test, y_pred, target_names=target_names))

# =====================
# CONFUSION MATRIX
# =====================

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=target_names, 
            yticklabels=target_names)
plt.title("Improved Attack Classification Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.tight_layout()
plt.show()

model.save_model(MODEL_SAVE_PATH)
print(f"Model saved to {MODEL_SAVE_PATH}")
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# =====================
# LOAD DATA
# =====================
DATA_PATH = "data/window_features.csv"
df = pd.read_csv(DATA_PATH)

# ---------------------
# Separate features & labels
# ---------------------
X = df.drop(columns=["label", "run_id"])
y = df["label"]

# =====================
# TRAIN / TEST SPLIT
# =====================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# =====================
# MODEL
# =====================
model = xgb.XGBClassifier(
    objective="multi:softprob",
    num_class=3,
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="mlogloss",
    random_state=42
)

# =====================
# TRAIN
# =====================
model.fit(X_train, y_train)

# =====================
# EVALUATE
# =====================
y_pred = model.predict(X_test)

print("\n=== Classification Report ===")
print(classification_report(
    y_test,
    y_pred,
    target_names=["Normal", "Fault", "Attack"]
))

# =====================
# CONFUSION MATRIX
# =====================
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Normal", "Fault", "Attack"],
    yticklabels=["Normal", "Fault", "Attack"]
)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("XGBoost Confusion Matrix")
plt.tight_layout()
plt.show()

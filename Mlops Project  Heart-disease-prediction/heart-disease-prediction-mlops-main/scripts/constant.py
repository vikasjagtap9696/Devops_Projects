
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier


MODEL_REGISTRY = {
    "DecisionTreeClassifier": DecisionTreeClassifier,
    "RandomForestClassifier": RandomForestClassifier,
    "LogisticRegression": LogisticRegression,
    "SVC": SVC,
    "GradientBoostingClassifier": GradientBoostingClassifier,
    "XGBClassifier": XGBClassifier,
    "KNN": KNeighborsClassifier,
    "MLPClassifier": MLPClassifier,
}

NUMERICAL_COLS = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_COLS = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]

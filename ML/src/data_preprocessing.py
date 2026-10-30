"""
Smart Disease Risk Prediction System
Module: src/data_preprocessing.py

Data cleaning, validation, and feature preprocessing pipeline.
Fits preprocessing transformers strictly on training data to avoid data leakage.
"""

from pathlib import Path
from typing import Tuple, List
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

# Canonical 11 Feature Schema in exact sequence
NUMERICAL_FEATURES: List[str] = [
    "age",
    "blood_pressure",
    "heart_rate",
    "glucose",
    "cholesterol",
    "bmi",
]

CATEGORICAL_FEATURES: List[str] = [
    "gender",
    "smoking",
    "physical_activity",
    "family_history",
    "heart_disease",
]

ALL_FEATURE_COLUMNS: List[str] = [
    "age",
    "gender",
    "blood_pressure",
    "heart_rate",
    "glucose",
    "cholesterol",
    "bmi",
    "smoking",
    "physical_activity",
    "family_history",
    "heart_disease",
]

TARGET_COLUMN: str = "target"


def create_preprocessor() -> ColumnTransformer:
    """
    Constructs a ColumnTransformer that applies:
      - Median imputation and standard scaling to numerical features.
      - Most-frequent imputation and one-hot encoding to categorical features.

    Returns:
    --------
    ColumnTransformer
        Unfitted scikit-learn ColumnTransformer.
    """
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(
                    sparse_output=False,
                    handle_unknown="ignore",
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERICAL_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    return preprocessor


def get_feature_names_from_preprocessor(preprocessor: ColumnTransformer) -> List[str]:
    """
    Extracts transformed feature names from fitted ColumnTransformer.
    """
    if hasattr(preprocessor, "get_feature_names_out"):
        return list(preprocessor.get_feature_names_out())
    # Fallback if un-fitted
    return NUMERICAL_FEATURES + CATEGORICAL_FEATURES


def load_and_clean_data(csv_path: Path) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Loads raw CSV dataset, validates required columns, eliminates duplicates,
    and separates feature matrix X from target vector y.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {csv_path}. Please execute 'python src/generate_dataset.py' first."
        )

    df = pd.read_csv(csv_path)

    # Validate columns
    missing_features = [col for col in ALL_FEATURE_COLUMNS if col not in df.columns]
    if missing_features:
        raise ValueError(f"Dataset is missing required feature columns: {missing_features}")

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Dataset is missing required target column: '{TARGET_COLUMN}'")

    # Drop duplicate rows
    df = df.drop_duplicates().reset_index(drop=True)

    # Enforce exact column ordering for X
    X = df[ALL_FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].astype(int).copy()

    return X, y


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.20,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Partitions features and labels into stratified training and testing splits.
    """
    return train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=random_state,
    )

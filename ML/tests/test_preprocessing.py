"""
Unit Tests: Data Preprocessing & Validation Pipeline
Module: tests/test_preprocessing.py
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_preprocessing import (
    load_and_clean_data,
    create_preprocessor,
    split_data,
    get_feature_names_from_preprocessor,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    ALL_FEATURE_COLUMNS,
)


@pytest.fixture
def dataset_path():
    """Provides path to generated disease dataset."""
    return PROJECT_ROOT / "data" / "disease_data.csv"


def test_load_and_clean_data(dataset_path):
    """Verifies dataset loads properly with required feature schema and target."""
    assert dataset_path.exists(), "Dataset file must exist before testing."
    X, y = load_and_clean_data(dataset_path)

    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)
    assert len(X) >= 1000
    assert len(X) == len(y)
    assert set(ALL_FEATURE_COLUMNS).issubset(set(X.columns))
    assert set(y.unique()).issubset({0, 1})


def test_missing_column_validation(tmp_path):
    """Tests that missing required features trigger a descriptive ValueError."""
    bad_csv = tmp_path / "bad_data.csv"
    bad_df = pd.DataFrame({"age": [45, 50], "target": [0, 1]})
    bad_df.to_csv(bad_csv, index=False)

    with pytest.raises(ValueError) as excinfo:
        load_and_clean_data(bad_csv)
    assert "missing required feature columns" in str(excinfo.value)


def test_stratified_split(dataset_path):
    """Verifies stratified split preserves target class proportions in train and test sets."""
    X, y = load_and_clean_data(dataset_path)
    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.20, random_state=42)

    assert len(X_train) == int(len(X) * 0.80)
    assert len(X_test) == int(len(X) * 0.20)

    # Check stratification
    train_ratio = y_train.mean()
    test_ratio = y_test.mean()
    assert abs(train_ratio - test_ratio) < 0.02


def test_column_transformer_fit_transform(dataset_path):
    """Verifies ColumnTransformer transforms all features without producing any NaN values."""
    X, y = load_and_clean_data(dataset_path)
    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.20, random_state=42)

    preprocessor = create_preprocessor()
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    assert isinstance(X_train_trans, np.ndarray)
    assert isinstance(X_test_trans, np.ndarray)
    assert not np.isnan(X_train_trans).any(), "Transformed train array contains NaNs."
    assert not np.isnan(X_test_trans).any(), "Transformed test array contains NaNs."
    assert X_train_trans.shape[1] == X_test_trans.shape[1]

    feature_names = get_feature_names_from_preprocessor(preprocessor)
    assert len(feature_names) == X_train_trans.shape[1]

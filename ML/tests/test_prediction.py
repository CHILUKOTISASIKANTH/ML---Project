"""
Unit Tests: Model Inference, Input Validation & Ensemble Predictions
Module: tests/test_prediction.py
"""

import sys
from pathlib import Path
import pytest

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.prediction import (
    load_trained_artifacts,
    validate_patient_input,
    predict_patient_risk,
)


def test_load_trained_artifacts():
    """Verifies that all required trained model pkl files are loaded into memory."""
    artifacts = load_trained_artifacts()
    expected_keys = [
        "preprocessor",
        "ensemble",
        "logistic_regression",
        "decision_tree",
        "random_forest",
        "svm",
    ]
    for key in expected_keys:
        assert key in artifacts, f"Artifact '{key}' must be present in loaded registry."


def test_healthy_patient_prediction():
    """Verifies a healthy baseline patient profile yields Low Risk."""
    healthy_input = {
        "age": 25,
        "gender": "Female",
        "blood_pressure": 112,
        "glucose": 85,
        "cholesterol": 165,
        "bmi": 21.0,
        "heart_rate": 65,
        "smoking": "Never",
        "physical_activity": "High",
        "family_history": "No",
        "heart_disease": "No",
    }

    result = predict_patient_risk(healthy_input)
    assert result["success"] is True
    assert result["risk_label"] == "LOW RISK"
    assert result["high_risk_prob"] < 50.0
    assert 0.0 <= result["high_risk_prob"] <= 100.0
    assert len(result["individual_predictions"]) == 5


def test_high_risk_patient_prediction():
    """Verifies an at-risk profile with severe comorbidities yields High Risk."""
    high_risk_input = {
        "age": 70,
        "gender": "Male",
        "blood_pressure": 168,
        "glucose": 190,
        "cholesterol": 270,
        "bmi": 34.5,
        "heart_rate": 92,
        "smoking": "Current",
        "physical_activity": "Low",
        "family_history": "Yes",
        "heart_disease": "Yes",
    }

    result = predict_patient_risk(high_risk_input)
    assert result["success"] is True
    assert result["risk_label"] == "HIGH RISK"
    assert result["high_risk_prob"] >= 50.0
    assert 0.0 <= result["high_risk_prob"] <= 100.0


def test_former_smoker_other_gender_prediction():
    """Verifies Former smoking and Other gender are handled seamlessly by the inference pipeline."""
    moderate_input = {
        "age": 52,
        "gender": "Other",
        "blood_pressure": 130,
        "glucose": 110,
        "cholesterol": 205,
        "bmi": 26.5,
        "heart_rate": 74,
        "smoking": "Former",
        "physical_activity": "Moderate",
        "family_history": "Yes",
        "heart_disease": "No",
    }

    result = predict_patient_risk(moderate_input)
    assert result["success"] is True
    assert result["risk_label"] in ["LOW RISK", "HIGH RISK"]
    assert 0.0 <= result["high_risk_prob"] <= 100.0


def test_invalid_input_validation():
    """Verifies out-of-range or malformed inputs are caught and return descriptive error messages."""
    invalid_input = {
        "age": -5,  # Out of range
        "gender": "Alien",  # Invalid categorical
        "blood_pressure": 350,  # Out of range
        "glucose": "abc",  # Not a number
        "cholesterol": 180,
        "bmi": 22.0,
        "heart_rate": 70,
        "smoking": "Never",
        "physical_activity": "High",
        "family_history": "No",
        "diabetes": "No",
        "hypertension": "No",
        "heart_disease": "No",
    }

    cleaned, errors = validate_patient_input(invalid_input)
    assert len(errors) >= 3
    assert any("Age" in e for e in errors)
    assert any("Gender" in e for e in errors)
    assert any("Blood Pressure" in e for e in errors)

    res = predict_patient_risk(invalid_input)
    assert res["success"] is False
    assert len(res["errors"]) >= 3

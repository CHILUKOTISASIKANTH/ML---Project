"""
Smart Disease Risk Prediction System
Module: src/prediction.py

Patient input validation, preprocessing, and multi-model risk classification.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List
import json
import joblib
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_preprocessing import ALL_FEATURE_COLUMNS

# Validation rules for form inputs
VALIDATION_RULES = {
    "age":             {"type": "int",         "min": 1,   "max": 120,  "label": "Age (years)"},
    "blood_pressure":  {"type": "float",        "min": 50.0, "max": 260.0, "label": "Systolic Blood Pressure (mmHg)"},
    "heart_rate":      {"type": "int",         "min": 30,  "max": 220,  "label": "Resting Heart Rate (bpm)"},
    "glucose":         {"type": "float",        "min": 40.0, "max": 450.0, "label": "Fasting Glucose (mg/dL)"},
    "cholesterol":     {"type": "float",        "min": 80.0, "max": 500.0, "label": "Total Cholesterol (mg/dL)"},
    "bmi":             {"type": "float",        "min": 10.0, "max": 75.0,  "label": "Body Mass Index (BMI)"},
    "gender":          {"type": "categorical",  "allowed": ["Male", "Female", "Other"],      "label": "Gender"},
    "smoking":         {"type": "categorical",  "allowed": ["Never", "Former", "Current"],   "label": "Smoking Status"},
    "physical_activity": {"type": "categorical","allowed": ["Low", "Moderate", "High"],      "label": "Physical Activity Level"},
    "family_history":  {"type": "categorical",  "allowed": ["No", "Yes"],                    "label": "Family History"},
    "heart_disease":   {"type": "categorical",  "allowed": ["No", "Yes"],                    "label": "Prior Heart Disease"},
}


class ModelRegistry:
    """Singleton to cache trained models and artifacts in memory across requests."""
    _artifacts = None

    @classmethod
    def get_artifacts(cls) -> Dict[str, Any]:
        if cls._artifacts is None:
            cls._artifacts = load_trained_artifacts()
        return cls._artifacts

    @classmethod
    def reload(cls):
        cls._artifacts = None


def load_trained_artifacts() -> Dict[str, Any]:
    """
    Loads all trained model pipelines and evaluation metrics from models/ directory.
    Raises FileNotFoundError if artifacts have not been generated yet.
    """
    models_dir = PROJECT_ROOT / "models"

    required_files = {
        "preprocessor":          models_dir / "preprocessor.pkl",
        "ensemble":              models_dir / "ensemble.pkl",
        "logistic_regression":   models_dir / "logistic_regression.pkl",
        "decision_tree":         models_dir / "decision_tree.pkl",
        "random_forest":         models_dir / "random_forest.pkl",
        "svm":                   models_dir / "svm.pkl",
    }

    missing = [name for name, path in required_files.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing model files: {', '.join(missing)}.\n"
            f"Run 'python src/train_models.py' first."
        )

    artifacts = {}
    for name, path in required_files.items():
        artifacts[name] = joblib.load(path)

    # Load evaluation metrics if present
    metrics_file = models_dir / "evaluation_results.json"
    if metrics_file.exists():
        with open(metrics_file, "r", encoding="utf-8") as f:
            artifacts["evaluation_results"] = json.load(f)
    else:
        artifacts["evaluation_results"] = {}

    return artifacts


def validate_patient_input(raw_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validates and converts patient form inputs.

    Returns:
    --------
    Tuple[Dict[str, Any], List[str]]
        (cleaned_dict, list_of_errors)
    """
    cleaned: Dict[str, Any] = {}
    errors: List[str] = []

    for field, rule in VALIDATION_RULES.items():
        val = raw_data.get(field)
        label = rule["label"]

        if val is None or str(val).strip() == "":
            errors.append(f"Required field missing: '{label}'.")
            continue

        str_val = str(val).strip()

        if rule["type"] == "int":
            try:
                num = int(float(str_val))
                if num < rule["min"] or num > rule["max"]:
                    errors.append(f"{label}: value {num} is outside allowed range ({rule['min']} – {rule['max']}).")
                else:
                    cleaned[field] = num
            except ValueError:
                errors.append(f"{label}: must be a whole number.")

        elif rule["type"] == "float":
            try:
                num = round(float(str_val), 2)
                if num < rule["min"] or num > rule["max"]:
                    errors.append(f"{label}: value {num} is outside allowed range ({rule['min']} – {rule['max']}).")
                else:
                    cleaned[field] = num
            except ValueError:
                errors.append(f"{label}: must be a numeric value.")

        elif rule["type"] == "categorical":
            allowed = rule["allowed"]
            matched = next((a for a in allowed if a.lower() == str_val.lower()), None)
            if matched is None:
                errors.append(f"{label}: '{str_val}' is not a valid option. Choose from: {', '.join(allowed)}.")
            else:
                cleaned[field] = matched

    return cleaned, errors


def identify_risk_factors(patient: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Identifies notable risk indicators present in the patient's data.
    Used for informational breakdown on the result page.
    """
    flags = []

    age = patient.get("age", 0)
    bp = patient.get("blood_pressure", 0)
    glucose = patient.get("glucose", 0)
    cholesterol = patient.get("cholesterol", 0)
    bmi = patient.get("bmi", 0)
    smoking = patient.get("smoking", "")
    activity = patient.get("physical_activity", "")
    heart_disease = patient.get("heart_disease", "No")
    family_history = patient.get("family_history", "No")

    if age >= 60:
        flags.append({"factor": "Age 60+", "detail": f"Age {age} — cardiovascular risk tends to increase with age.", "severity": "moderate"})

    if bp >= 140:
        flags.append({"factor": "Elevated Systolic BP", "detail": f"Systolic BP: {bp} mmHg (≥140 mmHg).", "severity": "high"})
    elif bp >= 130:
        flags.append({"factor": "Raised Systolic BP", "detail": f"Systolic BP: {bp} mmHg (130–139 mmHg).", "severity": "moderate"})

    if glucose >= 140:
        flags.append({"factor": "High Fasting Glucose", "detail": f"Fasting glucose: {glucose} mg/dL (≥140 mg/dL).", "severity": "high"})
    elif glucose >= 100:
        flags.append({"factor": "Elevated Glucose", "detail": f"Fasting glucose: {glucose} mg/dL (100–139 mg/dL).", "severity": "moderate"})

    if cholesterol >= 240:
        flags.append({"factor": "High Total Cholesterol", "detail": f"Cholesterol: {cholesterol} mg/dL (≥240 mg/dL).", "severity": "high"})
    elif cholesterol >= 200:
        flags.append({"factor": "Borderline Cholesterol", "detail": f"Cholesterol: {cholesterol} mg/dL (200–239 mg/dL).", "severity": "moderate"})

    if bmi >= 30:
        flags.append({"factor": "BMI in Obese Range", "detail": f"BMI: {bmi} kg/m² (≥30).", "severity": "high"})
    elif bmi >= 25:
        flags.append({"factor": "BMI in Overweight Range", "detail": f"BMI: {bmi} kg/m² (25–29.9).", "severity": "moderate"})

    if smoking == "Current":
        flags.append({"factor": "Current Smoker", "detail": "Current smoking status.", "severity": "high"})
    elif smoking == "Former":
        flags.append({"factor": "Former Smoker", "detail": "Previous smoking history recorded.", "severity": "low"})

    if activity == "Low":
        flags.append({"factor": "Low Physical Activity", "detail": "Sedentary activity level.", "severity": "moderate"})

    if heart_disease == "Yes":
        flags.append({"factor": "Prior Heart Disease", "detail": "History of heart disease recorded.", "severity": "high"})

    if family_history == "Yes":
        flags.append({"factor": "Family History", "detail": "Family history of cardiovascular or metabolic disease.", "severity": "moderate"})

    if not flags:
        flags.append({"factor": "No Notable Risk Flags", "detail": "Entered values are within typical reference ranges.", "severity": "positive"})

    return flags


def predict_patient_risk(raw_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full prediction pipeline:
      1. Validate and clean patient input
      2. Build DataFrame in feature order
      3. Run Ensemble and individual model pipelines
      4. Compute predictions and probabilities
      5. Build consensus/disagreement analysis
      6. Identify risk factors

    Returns:
    --------
    Dict[str, Any]
        Results bundle for the result page template.
    """
    cleaned_data, errors = validate_patient_input(raw_input)
    if errors:
        return {"success": False, "errors": errors}

    try:
        artifacts = ModelRegistry.get_artifacts()
    except FileNotFoundError as e:
        return {"success": False, "errors": [str(e)]}

    ensemble = artifacts["ensemble"]
    individual_models = {
        "Logistic Regression": artifacts["logistic_regression"],
        "Decision Tree":       artifacts["decision_tree"],
        "Random Forest":       artifacts["random_forest"],
        "Support Vector Machine": artifacts["svm"],
    }

    # Build single-row DataFrame matching ALL_FEATURE_COLUMNS order
    input_df = pd.DataFrame([cleaned_data])[ALL_FEATURE_COLUMNS]

    # 1. Ensemble Prediction (Primary)
    ens_pred = int(ensemble.predict(input_df)[0])
    ens_probs = ensemble.predict_proba(input_df)[0]
    high_risk_prob = float(ens_probs[1]) * 100.0
    low_risk_prob = float(ens_probs[0]) * 100.0
    risk_label = "HIGH RISK" if ens_pred == 1 else "LOW RISK"

    # 2. Individual Model Predictions
    breakdown = []
    votes_high = 0
    votes_low = 0

    for name, model in individual_models.items():
        m_pred = int(model.predict(input_df)[0])
        if hasattr(model, "predict_proba"):
            m_prob = float(model.predict_proba(input_df)[0][1]) * 100.0
        else:
            m_prob = 100.0 if m_pred == 1 else 0.0

        m_label = "High Risk" if m_pred == 1 else "Low Risk"
        if m_pred == 1:
            votes_high += 1
        else:
            votes_low += 1

        breakdown.append({
            "model_name": name,
            "prediction": m_label,
            "is_high_risk": m_pred == 1,
            "probability": round(m_prob, 1),
        })

    # Also add ensemble to the full breakdown for display
    breakdown.append({
        "model_name": "Ensemble",
        "prediction": "High Risk" if ens_pred == 1 else "Low Risk",
        "is_high_risk": ens_pred == 1,
        "probability": round(high_risk_prob, 1),
    })

    # 3. Consensus analysis (based on individual models only)
    total_models = len(individual_models)
    if votes_high == total_models:
        consensus_text = "All configured models produced the same classification: High Risk."
        consensus_type = "unanimous_high"
    elif votes_low == total_models:
        consensus_text = "All configured models produced the same classification: Low Risk."
        consensus_type = "unanimous_low"
    else:
        consensus_text = (
            f"Model predictions differ for this assessment. "
            f"{votes_high} model(s) classified High Risk and {votes_low} classified Low Risk. "
            f"The Ensemble resolves this by averaging probabilities across all models."
        )
        consensus_type = "disagreement"

    # 4. Risk Factors
    risk_factors = identify_risk_factors(cleaned_data)

    # 5. Plain interpretation text
    if ens_pred == 1:
        interpretation = (
            f"The Ensemble model classified this profile as High Risk with an estimated "
            f"high-risk probability of {high_risk_prob:.1f}%. "
            f"The classification is based on the values entered and patterns learned from the training dataset."
        )
    else:
        interpretation = (
            f"The Ensemble model classified this profile as Low Risk with an estimated "
            f"high-risk probability of {high_risk_prob:.1f}%. "
            f"The classification is based on the values entered and patterns learned from the training dataset."
        )

    return {
        "success": True,
        "patient_input": cleaned_data,
        "risk_label": risk_label,
        "is_high_risk": ens_pred == 1,
        "high_risk_prob": round(high_risk_prob, 1),
        "low_risk_prob": round(low_risk_prob, 1),
        "individual_predictions": breakdown,
        "votes_high": votes_high,
        "votes_low": votes_low,
        "consensus_text": consensus_text,
        "consensus_type": consensus_type,
        "interpretation": interpretation,
        "risk_factors": risk_factors,
    }

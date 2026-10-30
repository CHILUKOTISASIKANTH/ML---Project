"""
Smart Disease Risk Prediction System
Module: src/generate_dataset.py

Generates reproducible synthetic dataset for machine learning risk classification.
Simulates realistic distributions and correlations between physiological measurements,
medical history, and cardio-metabolic risk.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def generate_synthetic_data(num_samples: int = 1500, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic patient medical records with correlated risk factors.

    Parameters:
    -----------
    num_samples : int
        Number of patient samples to generate (default: 1500).
    random_state : int
        Seed for reproducibility (default: 42).

    Returns:
    --------
    pd.DataFrame
        Synthetic patient health dataset with features and target column.
    """
    np.random.seed(random_state)

    # 1. Demographics
    age = np.random.randint(20, 85, size=num_samples)
    gender = np.random.choice(["Male", "Female", "Other"], size=num_samples, p=[0.49, 0.49, 0.02])

    # 2. Lifestyle & Genetic Factors
    # Smoking status: Never, Former, Current
    smoking = np.random.choice(
        ["Never", "Former", "Current"], size=num_samples, p=[0.55, 0.20, 0.25]
    )

    # Physical activity level: Low, Moderate, High
    physical_activity = np.random.choice(
        ["Low", "Moderate", "High"], size=num_samples, p=[0.40, 0.40, 0.20]
    )

    # Family history of cardiovascular or metabolic disease
    family_history = np.random.choice(["No", "Yes"], size=num_samples, p=[0.60, 0.40])

    # 3. Medical History & Genetic Factors
    hd_prob = 0.04 + (age / 180.0) + np.where(smoking == "Current", 0.08, 0.0)
    hd_prob = np.clip(hd_prob, 0.02, 0.50)
    heart_disease = np.where(np.random.rand(num_samples) < hd_prob, "Yes", "No")

    # 4. Vital Signs & Laboratory Biomarkers
    # Systolic Blood Pressure (mmHg): baseline ~122, elevated with age and low physical activity
    bp_base = np.random.normal(120, 11, size=num_samples)
    bp_lifestyle = ((age - 35) * 0.35) + np.where(physical_activity == "Low", 7.0, 0.0)
    blood_pressure = np.round(np.clip(bp_base + bp_lifestyle, 90, 195), 1)

    # Resting Heart Rate (bpm): baseline ~72, higher if smoking, lower if active
    hr_base = np.random.normal(72, 8, size=num_samples)
    hr_lifestyle = np.where(smoking == "Current", 5.0, 0) - np.where(physical_activity == "High", 4.0, 0)
    heart_rate = np.round(np.clip(hr_base + hr_lifestyle, 50, 115), 0).astype(int)

    # Fasting Glucose (mg/dL): baseline ~96, elevated with age, BMI, and low activity
    glucose_base = np.random.normal(95, 12, size=num_samples)
    glucose_lifestyle = ((age - 40) * 0.40) + np.where(physical_activity == "Low", 14.0, 0.0)
    glucose = np.round(np.clip(glucose_base + glucose_lifestyle, 70, 285), 1)

    # Total Cholesterol (mg/dL): baseline ~185, influenced by age and activity
    chol_base = np.random.normal(185, 22, size=num_samples)
    chol_lifestyle = np.where(physical_activity == "Low", 18, 0) + ((age - 40) * 0.25)
    cholesterol = np.round(np.clip(chol_base + chol_lifestyle, 120, 330), 1)

    # Body Mass Index (BMI in kg/m2): baseline ~25.0, influenced by lifestyle
    bmi_base = np.random.normal(25.0, 4.2, size=num_samples)
    bmi_lifestyle = np.where(physical_activity == "Low", 2.2, 0)
    bmi = np.round(np.clip(bmi_base + bmi_lifestyle, 16.5, 45.0), 1)

    # 5. Composite Latent Risk Score Calculation
    latent_score = (
        (age - 52) * 0.040
        + (blood_pressure - 128) * 0.045
        + (heart_rate - 72) * 0.018
        + (glucose - 105) * 0.040
        + (cholesterol - 200) * 0.020
        + (bmi - 26) * 0.055
        + np.where(smoking == "Current", 0.95, np.where(smoking == "Former", 0.30, -0.40))
        + np.where(physical_activity == "Low", 0.65, np.where(physical_activity == "High", -0.80, 0.0))
        + np.where(family_history == "Yes", 0.75, -0.30)
        + np.where(heart_disease == "Yes", 1.65, -0.50)
        + np.random.normal(0, 0.85, size=num_samples)
    )

    # Binary Classification Target: 0 = Low Risk, 1 = High Risk (Balanced at median)
    threshold = float(np.median(latent_score))
    target = (latent_score >= threshold).astype(int)

    # 6. Assemble DataFrame in exact 11 feature order + target
    df = pd.DataFrame(
        {
            "age": age,
            "gender": gender,
            "blood_pressure": blood_pressure,
            "heart_rate": heart_rate,
            "glucose": glucose,
            "cholesterol": cholesterol,
            "bmi": bmi,
            "smoking": smoking,
            "physical_activity": physical_activity,
            "family_history": family_history,
            "heart_disease": heart_disease,
            "target": target,
        }
    )

    return df


def main():
    """Generates the dataset and saves to data/disease_data.csv."""
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    output_path = data_dir / "disease_data.csv"

    print("=" * 60)
    print("Generating Synthetic Health Risk Dataset...")
    print("=" * 60)

    df = generate_synthetic_data(num_samples=1500, random_state=42)
    df.to_csv(output_path, index=False)

    print(f"Dataset successfully saved to:\n  {output_path}")
    print(f"Total Records: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print("\nClass Distribution:")
    print(df["target"].value_counts(normalize=True).apply(lambda x: f"{x:.2%}"))
    print("\nColumns:")
    print(list(df.columns))
    print("=" * 60)


if __name__ == "__main__":
    main()

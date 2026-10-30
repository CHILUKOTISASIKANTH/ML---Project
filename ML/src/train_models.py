"""
Smart Disease Risk Prediction System
Module: src/train_models.py

End-to-end model training pipeline:
  1. Load and clean data from data/disease_data.csv
  2. Stratified 80/20 train/test split
  3. Fit preprocessor on training data (no data leakage)
  4. Train Logistic Regression, Decision Tree, Random Forest, SVM
  5. Build and train Soft Voting Ensemble
  6. Evaluate all models on held-out test set
  7. Save model pipelines to models/
  8. Generate evaluation charts to static/images/
  9. Save metrics to models/evaluation_results.json
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC

from src.data_preprocessing import (
    load_and_clean_data,
    create_preprocessor,
    split_data,
    get_feature_names_from_preprocessor,
    ALL_FEATURE_COLUMNS,
)
from src.evaluate_models import (
    evaluate_single_model,
    plot_confusion_matrix,
    plot_model_comparison,
    plot_roc_curves,
    plot_feature_importance,
    save_evaluation_results,
)


def build_pipeline(classifier, preprocessor):
    """Wraps a preprocessor and classifier in a sklearn Pipeline."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier),
    ])


def train_and_evaluate_all():
    """Orchestrates complete model training, evaluation, and artifact generation."""
    project_root = Path(__file__).resolve().parent.parent
    data_path = project_root / "data" / "disease_data.csv"
    models_dir = project_root / "models"
    images_dir = project_root / "static" / "images"

    models_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  SMART DISEASE RISK PREDICTION SYSTEM — MODEL TRAINING PIPELINE")
    print("=" * 70)

    # 1. Load Data
    print(f"\n[1/6] Loading dataset from: {data_path}")
    X, y = load_and_clean_data(data_path)
    print(f"      Loaded {len(X)} samples with {X.shape[1]} features.")
    print(f"      Feature order: {list(X.columns)}")
    print(f"      Class distribution: {dict(y.value_counts())}")

    # 2. Train/Test Split (Stratified 80/20)
    print("\n[2/6] Splitting into 80% Train / 20% Test (stratified)...")
    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.20, random_state=42)
    print(f"      Training: {len(X_train)} samples | Testing: {len(X_test)} samples")

    # 3. Fit Preprocessor on Training Data Only
    print("\n[3/6] Fitting preprocessor on training data...")
    preprocessor_fitted = create_preprocessor()
    preprocessor_fitted.fit(X_train)
    feature_names = get_feature_names_from_preprocessor(preprocessor_fitted)
    X_test_trans = preprocessor_fitted.transform(X_test)
    print(f"      Transformed features ({len(feature_names)}): {', '.join(feature_names)}")

    # Save fitted preprocessor separately
    joblib.dump(preprocessor_fitted, models_dir / "preprocessor.pkl")
    print(f"      Saved preprocessor to models/preprocessor.pkl")

    # 4. Define and Train Baseline Classifiers
    print("\n[4/6] Training 4 baseline classifiers...")
    classifiers = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, C=1.0, solver="lbfgs", random_state=42
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=5, min_samples_split=10, min_samples_leaf=5, random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=6, min_samples_split=8, random_state=42
        ),
        "Support Vector Machine": CalibratedClassifierCV(
            SVC(C=1.0, kernel="rbf", random_state=42), ensemble=False
        ),
    }

    # Build pipelines and train
    pipelines = {}
    for name, clf in classifiers.items():
        print(f"      Training {name}...")
        # Create a fresh preprocessor for each pipeline
        pipe = build_pipeline(clf, create_preprocessor())
        pipe.fit(X_train, y_train)
        pipelines[name] = pipe

    # 5. Build and Train Soft Voting Ensemble (using pipelines)
    print("\n[5/6] Building Soft Voting Ensemble...")
    ensemble = VotingClassifier(
        estimators=[
            ("lr", pipelines["Logistic Regression"]),
            ("dt", pipelines["Decision Tree"]),
            ("rf", pipelines["Random Forest"]),
            ("svm", pipelines["Support Vector Machine"]),
        ],
        voting="soft",
    )
    ensemble.fit(X_train, y_train)
    pipelines["Ensemble"] = ensemble
    print("      Ensemble trained successfully.")

    # 6. Evaluate All Models on Held-Out Test Data
    print("\n[6/6] Evaluating all models on 20% test set...")
    evaluation_results = {}

    cm_filenames = {
        "Logistic Regression": "confusion_matrix_logistic.png",
        "Decision Tree": "confusion_matrix_decision_tree.png",
        "Random Forest": "confusion_matrix_random_forest.png",
        "Support Vector Machine": "confusion_matrix_svm.png",
        "Ensemble": "confusion_matrix_ensemble.png",
    }

    print("\n" + "-" * 75)
    print(f"{'Model':<26} | {'Accuracy':>8} | {'Precision':>9} | {'Recall':>8} | {'F1':>6} | {'ROC-AUC':>8}")
    print("-" * 75)

    for name, model in pipelines.items():
        # For pipeline and VotingClassifier, pass raw X_test
        metrics = evaluate_single_model(model, X_test, y_test, name)
        evaluation_results[name] = metrics

        print(
            f"{name:<26} | {metrics['accuracy']:>8.4f} | {metrics['precision']:>9.4f} | "
            f"{metrics['recall']:>8.4f} | {metrics['f1_score']:>6.4f} | {metrics['roc_auc']:>8.4f}"
        )

        # Plot confusion matrix
        cm_fname = cm_filenames.get(name, f"confusion_matrix_{name.lower().replace(' ', '_')}.png")
        plot_confusion_matrix(metrics["confusion_matrix"], name, images_dir / cm_fname)

    print("-" * 75)

    # Generate comparison charts
    print("\nGenerating evaluation charts...")
    plot_model_comparison(evaluation_results, images_dir / "model_comparison.png")
    print("  -> Saved model_comparison.png")

    plot_roc_curves(evaluation_results, images_dir / "roc_curve.png")
    print("  -> Saved roc_curve.png")

    # Feature Importance from Random Forest pipeline
    rf_pipeline = pipelines["Random Forest"]
    rf_clf = rf_pipeline.named_steps["classifier"]
    rf_preprocessor = rf_pipeline.named_steps["preprocessor"]
    rf_feature_names = get_feature_names_from_preprocessor(rf_preprocessor)
    plot_feature_importance(
        rf_feature_names,
        rf_clf.feature_importances_,
        "Random Forest",
        images_dir / "feature_importance.png",
    )
    print("  -> Saved feature_importance.png")

    # Save all model pipelines
    model_file_map = {
        "Logistic Regression": "logistic_regression.pkl",
        "Decision Tree": "decision_tree.pkl",
        "Random Forest": "random_forest.pkl",
        "Support Vector Machine": "svm.pkl",
        "Ensemble": "ensemble.pkl",
    }

    for name, filename in model_file_map.items():
        save_path = models_dir / filename
        joblib.dump(pipelines[name], save_path)
        print(f"  -> Saved {filename}")

    # Save evaluation metrics JSON
    metrics_path = models_dir / "evaluation_results.json"
    save_evaluation_results(evaluation_results, metrics_path)
    print(f"\n  -> Saved evaluation_results.json")

    print("\n" + "=" * 70)
    print("  Training Pipeline Complete. All models and artifacts saved.")
    print("  Run 'python app.py' to start the web application.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    train_and_evaluate_all()

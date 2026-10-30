"""
Smart Disease Risk Prediction System
app.py — Flask Application Entry Point
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.prediction import (
    predict_patient_risk,
    load_trained_artifacts,
    ModelRegistry,
    VALIDATION_RULES,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "sdrs-project-secret-key-2026")


@app.context_processor
def inject_global_context():
    return {
        "app_name": "Smart Disease Risk Prediction System",
        "app_short": "Disease Risk",
    }


def check_models_ready():
    """Verifies that all required model .pkl files exist."""
    models_dir = PROJECT_ROOT / "models"
    required = [
        "ensemble.pkl",
        "logistic_regression.pkl",
        "decision_tree.pkl",
        "random_forest.pkl",
        "svm.pkl",
    ]
    return all((models_dir / f).exists() for f in required)


@app.route("/")
def index():
    models_ready = check_models_ready()
    return render_template("index.html", models_ready=models_ready)


@app.route("/assessment", methods=["GET"])
def assessment():
    models_ready = check_models_ready()
    if not models_ready:
        flash(
            "Trained models not found. Please run 'python src/train_models.py' first.",
            "warning",
        )
    return render_template(
        "assessment.html",
        models_ready=models_ready,
        form_data={},
        validation_rules=VALIDATION_RULES,
    )


@app.route("/predict", methods=["POST"])
def predict():
    """
    Processes POST form data, runs the prediction pipeline,
    and renders the result page.
    """
    models_ready = check_models_ready()
    if not models_ready:
        flash("Models not trained. Run 'python src/train_models.py' first.", "warning")
        return redirect(url_for("assessment"))

    raw_form = request.form.to_dict()

    try:
        results = predict_patient_risk(raw_form)

        if not results.get("success"):
            for err in results.get("errors", ["Invalid input received."]):
                flash(err, "danger")
            return render_template(
                "assessment.html",
                models_ready=True,
                form_data=raw_form,
                validation_rules=VALIDATION_RULES,
            )

        return render_template("result.html", results=results, models_ready=True)

    except FileNotFoundError as e:
        flash(str(e), "danger")
        return redirect(url_for("assessment"))
    except Exception as ex:
        flash(f"An error occurred during prediction: {str(ex)}", "danger")
        return redirect(url_for("assessment"))


@app.route("/models")
def models_comparison():
    models_ready = check_models_ready()
    metrics_data = {}

    if models_ready:
        try:
            artifacts = ModelRegistry.get_artifacts()
            metrics_data = artifacts.get("evaluation_results", {})
        except Exception as e:
            flash(f"Could not load evaluation metrics: {str(e)}", "warning")

    return render_template(
        "models.html",
        models_ready=models_ready,
        metrics=metrics_data,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    print("=" * 65)
    print("  Smart Disease Risk Prediction System")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=True)

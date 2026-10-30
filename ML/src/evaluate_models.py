"""
Smart Disease Risk Prediction System
Module: src/evaluate_models.py

Model evaluation, metrics computation, and chart generation.
Generates confusion matrices, ROC curves, feature importance, and performance charts.
"""

from pathlib import Path
from typing import Dict, Any, List
import json
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend safe for Windows/web servers
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
)


def evaluate_single_model(
    model: Any,
    X_test: Any,
    y_test: np.ndarray,
    model_name: str,
) -> Dict[str, Any]:
    """
    Computes test metrics for a fitted model or pipeline on held-out test data.

    Parameters:
    -----------
    model : Any
        Trained model or pipeline.
    X_test : Any
        Test features (raw DataFrame if pipeline, transformed array if standalone model).
    y_test : np.ndarray
        Ground-truth binary labels.
    model_name : str
        Display name of the model.

    Returns:
    --------
    Dict[str, Any]
        Dictionary containing accuracy, precision, recall, f1_score, roc_auc, confusion_matrix, etc.
    """
    y_pred = model.predict(X_test)

    # Calculate probabilities for class 1 (High Risk)
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
    elif hasattr(model, "decision_function"):
        df_vals = model.decision_function(X_test)
        y_prob = 1.0 / (1.0 + np.exp(-df_vals))
    else:
        y_prob = y_pred.astype(float)

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))

    try:
        auc = float(roc_auc_score(y_test, y_prob))
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        fpr_list = fpr.tolist()
        tpr_list = tpr.tolist()
    except Exception:
        auc = 0.5
        fpr_list, tpr_list = [0.0, 1.0], [0.0, 1.0]

    cm = confusion_matrix(y_test, y_pred).tolist()

    return {
        "model_name": model_name,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": auc,
        "confusion_matrix": cm,
        "y_prob": y_prob,
        "fpr": fpr_list,
        "tpr": tpr_list,
    }


def plot_confusion_matrix(cm: List[List[int]], model_name: str, save_path: Path):
    """
    Plots a clean, professional confusion matrix heatmap.
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(4.8, 4.0), dpi=160)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=["Low Risk", "High Risk"],
        yticklabels=["Low Risk", "High Risk"],
        annot_kws={"size": 13, "weight": "bold", "color": "#1e293b"},
        linewidths=0.5,
        linecolor="#cbd5e1",
        ax=ax,
    )
    ax.set_title(f"Confusion Matrix: {model_name}", fontsize=11, pad=10, weight="bold", color="#0f172a")
    ax.set_xlabel("Predicted Label", fontsize=10, labelpad=8, color="#334155")
    ax.set_ylabel("Actual Label", fontsize=10, labelpad=8, color="#334155")
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)


def plot_model_comparison(metrics_dict: Dict[str, Dict[str, Any]], save_path: Path):
    """
    Plots grouped bar chart comparing performance metrics across all models.
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    model_names = list(metrics_dict.keys())
    metric_keys = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]

    x = np.arange(len(model_names))
    width = 0.15

    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=160)
    colors = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#0891b2"]

    for i, (key, label) in enumerate(zip(metric_keys, metric_labels)):
        values = [metrics_dict[m][key] for m in model_names]
        ax.bar(
            x + (i - 2) * width,
            values,
            width,
            label=label,
            color=colors[i],
            edgecolor="#ffffff",
            linewidth=0.8,
        )

    ax.set_xlabel("Classification Models", fontsize=11, labelpad=10, weight="bold", color="#0f172a")
    ax.set_ylabel("Score (0.0 to 1.0)", fontsize=11, labelpad=10, weight="bold", color="#0f172a")
    ax.set_title("Model Comparison on Test Set", fontsize=13, pad=14, weight="bold", color="#0f172a")
    ax.set_xticks(x)
    ax.set_xticklabels(model_names, fontsize=9.5, weight="bold", color="#1e293b")
    ax.set_ylim(0.5, 1.02)
    ax.grid(axis="y", linestyle="--", alpha=0.35, color="#94a3b8")
    ax.legend(loc="lower right", framealpha=0.95, fontsize=9.5)
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)


def plot_roc_curves(metrics_dict: Dict[str, Dict[str, Any]], save_path: Path):
    """
    Plots overlaid ROC curves for all models showing actual ROC-AUC.
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7.2, 5.5), dpi=160)
    ax.plot([0, 1], [0, 1], "k--", lw=1.2, alpha=0.6, label="Chance Baseline (AUC = 0.500)")

    colors = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#dc2626"]
    for idx, (m_name, m_data) in enumerate(metrics_dict.items()):
        fpr = m_data["fpr"]
        tpr = m_data["tpr"]
        auc_val = m_data["roc_auc"]
        color = colors[idx % len(colors)]
        ax.plot(fpr, tpr, lw=2.0, color=color, label=f"{m_name} (AUC = {auc_val:.3f})")

    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.05])
    ax.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=10.5, labelpad=8, color="#334155")
    ax.set_ylabel("True Positive Rate (Sensitivity)", fontsize=10.5, labelpad=8, color="#334155")
    ax.set_title("Receiver Operating Characteristic (ROC) Curves", fontsize=12.5, pad=12, weight="bold", color="#0f172a")
    ax.legend(loc="lower right", framealpha=0.95, fontsize=9)
    ax.grid(True, linestyle=":", alpha=0.5, color="#94a3b8")
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)


def plot_feature_importance(
    feature_names: List[str],
    importances: np.ndarray,
    model_name: str,
    save_path: Path,
):
    """
    Plots horizontal bar chart of Random Forest feature importance.
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Sort in ascending order for horizontal bar chart
    indices = np.argsort(importances)
    sorted_features = [feature_names[i] for i in indices]
    sorted_importances = importances[indices]

    fig, ax = plt.subplots(figsize=(8.0, 6.0), dpi=160)
    bars = ax.barh(sorted_features, sorted_importances, color="#1d4ed8", edgecolor="#ffffff", linewidth=0.6)

    # Annotate numeric values
    max_val = max(sorted_importances) if len(sorted_importances) > 0 else 0.1
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + (max_val * 0.015),
            bar.get_y() + bar.get_height() / 2,
            f"{width:.3f}",
            va="center",
            ha="left",
            fontsize=8.5,
            color="#1e293b",
            weight="bold",
        )

    ax.set_xlabel("Relative Importance (Gini)", fontsize=10.5, labelpad=8, weight="bold", color="#334155")
    ax.set_title(f"Model Feature Importance ({model_name})", fontsize=12.5, pad=12, weight="bold", color="#0f172a")
    ax.set_xlim(0, max_val * 1.18)
    ax.grid(axis="x", linestyle="--", alpha=0.4, color="#94a3b8")
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)


def save_evaluation_results(metrics_dict: Dict[str, Dict[str, Any]], output_json: Path):
    """
    Saves serializable evaluation dictionary to JSON.
    """
    output_json = Path(output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    serializable = {}
    for m_name, data in metrics_dict.items():
        serializable[m_name] = {
            "accuracy": round(data["accuracy"], 4),
            "precision": round(data["precision"], 4),
            "recall": round(data["recall"], 4),
            "f1_score": round(data["f1_score"], 4),
            "roc_auc": round(data["roc_auc"], 4),
            "confusion_matrix": data["confusion_matrix"],
        }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=4)

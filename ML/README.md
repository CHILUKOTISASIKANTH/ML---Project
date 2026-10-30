# Smart Disease Risk Prediction System
### Machine Learning-Based Health Risk Estimation & Multi-Model Ensemble

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.0+](https://img.shields.io/badge/Flask-3.0%2B-black.svg)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/pytest-9%20passed-brightgreen.svg)]()

---

## 1. Project Overview

The **Smart Disease Risk Prediction System** is a production-grade machine learning web application that predicts chronic disease risk from 11 physiological vitals, clinical measurements, and lifestyle factors.

The system trains and compares **four standalone classification algorithms** alongside a **Soft Voting Ensemble Meta-Classifier**:
1. **Logistic Regression** (L2-penalized linear classification)
2. **Decision Tree** (hierarchical binary partitioning, regularized depth)
3. **Random Forest** (ensemble of 100 decorrelated bagged decision trees)
4. **Support Vector Machine (SVM)** (RBF kernel with calibrated probability scaling)
5. **Soft Voting Ensemble** (consensus weighted probability aggregation)

### Core Outcomes:
- **Primary Binary Classification:** `LOW RISK` or `HIGH RISK`
- **Continuous Risk Probability:** Calibrated probability percentage (0% - 100%)
- **Multi-Model Predictions:** Transparent outputs from all 4 base models plus the ensemble
- **Model Consensus:** Identifies unanimous agreement or highlights differing model outputs
- **Clinical Parameter Review:** Categorizes patient inputs and identifies out-of-range biomarkers

---

## 2. Technology Stack

| Component | Technology | Role |
|---|---|---|
| **Language** | Python 3.10 - 3.13 | Core runtime |
| **Machine Learning** | scikit-learn | Preprocessing pipelines, models, ensemble, evaluation metrics |
| **Data Processing** | pandas, NumPy | Numerical processing and tabular transformations |
| **Visualization** | matplotlib, seaborn | ROC curves, confusion matrices, feature importance charts |
| **Serialization** | joblib | Artifact and model persistence |
| **Backend** | Flask | Routing, input validation, inference controller |
| **Frontend** | HTML5, Vanilla CSS, JavaScript | Responsive user interface, form validation, preset loading |
| **Testing** | pytest | Automated unit testing for preprocessing and inference |

---

## 3. Project Directory Structure

```text
ML/
│
├── app.py                      # Flask web application & route controller
├── requirements.txt            # Python dependencies
├── run_project.bat             # Windows runner script (venv setup, training, server launch)
├── README.md                   # System documentation
│
├── data/
│   └── disease_data.csv        # 1,500 patient records with 11 features + target
│
├── models/
│   ├── logistic_regression.pkl # Serialized Logistic Regression pipeline
│   ├── decision_tree.pkl       # Serialized Decision Tree pipeline
│   ├── random_forest.pkl       # Serialized Random Forest pipeline
│   ├── svm.pkl                 # Serialized Support Vector Machine pipeline
│   ├── ensemble.pkl            # Serialized Soft Voting Ensemble pipeline
│   ├── preprocessor.pkl        # Fitted scikit-learn ColumnTransformer
│   └── evaluation_results.json # Dynamically computed test evaluation metrics
│
├── src/
│   ├── __init__.py             # Python package marker
│   ├── generate_dataset.py     # Balanced medical dataset generator (1,500 samples)
│   ├── data_preprocessing.py   # Leak-free cleaning, imputation, scaling & encoding
│   ├── train_models.py         # End-to-end model training, evaluation & artifact export
│   ├── evaluate_models.py      # Metric computation & publication-grade chart generation
│   └── prediction.py           # Real-time inference engine, validation & consensus logic
│
├── templates/
│   ├── base.html               # Master layout with navbar, container & footer
│   ├── index.html              # Landing page with system overview and model cards
│   ├── assessment.html         # 4-section patient assessment form with presets & BMI calculator
│   ├── result.html             # Multi-model risk report, probability bar & parameter summary
│   ├── models.html             # Benchmark dashboard with dynamic table & evaluation charts
│   ├── about.html              # Comprehensive technical documentation & feature schema
│   ├── 404.html                # Custom Not Found error page
│   └── 500.html                # Custom Internal Server Error page
│
├── static/
│   ├── css/
│   │   └── style.css           # Clean, professional modern responsive stylesheet
│   ├── js/
│   │   └── script.js           # Client validation, preset auto-fill & BMI calculator
│   └── images/
│       ├── model_comparison.png         # Grouped bar chart comparing all 5 models
│       ├── roc_curve.png                # Multi-model Receiver Operating Characteristic plot
│       ├── feature_importance.png       # Random Forest Gini feature importances
│       ├── confusion_matrix_logistic.png
│       ├── confusion_matrix_decision_tree.png
│       ├── confusion_matrix_random_forest.png
│       ├── confusion_matrix_svm.png
│       └── confusion_matrix_ensemble.png
│
├── notebooks/
│   └── analysis.ipynb          # Exploratory Data Analysis & evaluation notebook
│
└── tests/
    ├── __init__.py             # Test package marker
    ├── test_preprocessing.py   # Tests for data loading, splitting, and preprocessor
    └── test_prediction.py      # Tests for model loading, inference, and error handling
```

---

## 4. Feature Schema & Permissible Ranges

The dataset and inference engine use **11 input features** organized into 4 logical sections:

| Section | Parameter | Type | Permissible Range / Values | Physiological Reference |
|---|---|---|---|---|
| **1. Demographics** | `age` | Integer | 1 - 120 | Patient age in years |
| | `gender` | Categorical | `Male`, `Female`, `Other` | Biological and demographic factor |
| **2. Vital Signs** | `blood_pressure` | Float | 50.0 - 260.0 mmHg | Systolic blood pressure |
| | `heart_rate` | Integer | 30 - 220 bpm | Resting heart rate |
| **3. Clinical Lab Values** | `glucose` | Float | 40.0 - 450.0 mg/dL | Fasting plasma glucose |
| | `cholesterol` | Float | 80.0 - 500.0 mg/dL | Total serum cholesterol |
| | `bmi` | Float | 10.0 - 75.0 kg/m² | Body Mass Index |
| **4. Lifestyle & History** | `smoking` | Categorical | `Never`, `Former`, `Current` | Cigarette smoking history |
| | `physical_activity` | Categorical | `Low`, `Moderate`, `High` | Weekly exercise activity level |
| | `family_history` | Categorical | `No`, `Yes` | Family history of chronic disease |
| | `heart_disease` | Categorical | `No`, `Yes` | Prior cardiovascular event |
| **Target** | `target` | Binary | `0` (Low Risk), `1` (High Risk) | Model classification target |

---

## 5. Quick Start & Execution Guide (Windows)

### Option A: One-Click Execution via Runner Script
Double-click `run_project.bat` or run:
```cmd
run_project.bat
```
The script automatically sets up the virtual environment, verifies dependencies, checks dataset and model artifacts, and launches the Flask server.

---

### Option B: Manual Step-by-Step Setup

#### 1. Navigate to Project Directory
```powershell
cd "c:\Users\chsas\OneDrive\SEM-4\Projects - 5\ML"
```

#### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Required Dependencies
```powershell
pip install -r requirements.txt
```

#### 4. Generate the Dataset
```powershell
python src/generate_dataset.py
```
Generates 1,500 patient records in `data/disease_data.csv`.

#### 5. Train Models and Generate Artifacts
```powershell
python src/train_models.py
```
Trains Logistic Regression, Decision Tree, Random Forest, SVM, and the Soft Voting Ensemble. Exports all `.pkl` pipelines to `models/`, generates 8 high-resolution charts in `static/images/`, and saves test set metrics to `models/evaluation_results.json`.

#### 6. Run Automated Unit Tests
```powershell
python -m pytest tests/
```
Runs all 9 unit tests across `tests/test_preprocessing.py` and `tests/test_prediction.py`.

#### 7. Launch the Flask Web Application
```powershell
python app.py
```
The application will be live at:
```text
http://127.0.0.1:5000
```

---

## 6. Model Evaluation Results

Evaluated on held-out **20% stratified test partition (300 patient samples)**:

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|---|---|---|---|---|---|
| **Logistic Regression** | 92.67% | 94.48% | 91.33% | 92.88% | 0.9849 |
| **Decision Tree** | 83.33% | 84.72% | 81.33% | 82.99% | 0.9266 |
| **Random Forest** | 91.33% | 92.57% | 91.33% | 91.95% | 0.9725 |
| **Support Vector Machine (SVM)** | 91.33% | 92.00% | 92.00% | 92.00% | 0.9802 |
| **Soft Voting Ensemble** | **91.00%** | **91.89%** | **91.33%** | **91.61%** | **0.9782** |

*Note: All metrics and confusion matrix graphics are recomputed dynamically during model training.*

---

## 7. Machine Learning Methodology

### Data Pipeline & Preprocessing:
1. **Data Leakage Prevention:** Data is split into 80% training and 20% test sets using stratified sampling before any transformations.
2. **Pipelines:** Each algorithm encapsulates its own `ColumnTransformer`:
   - **Numerical Features** (`age`, `blood_pressure`, `heart_rate`, `glucose`, `cholesterol`, `bmi`): Imputed with median and standardized using `StandardScaler`.
   - **Categorical Features** (`gender`, `smoking`, `physical_activity`, `family_history`, `diabetes`, `hypertension`, `heart_disease`): Imputed with most frequent and encoded using `OneHotEncoder(handle_unknown='ignore')`.

### Model Architectures:
- **Logistic Regression:** L2 regularized with L-BFGS solver.
- **Decision Tree:** Gini impurity splitting criterion, constrained depth (`max_depth=5`) to prevent overfitting.
- **Random Forest:** Ensemble of 100 estimators with `max_depth=6` and `min_samples_split=8`.
- **Support Vector Machine:** RBF kernel, calibrated with `CalibratedClassifierCV` for proper probabilistic confidence estimates.
- **Voting Ensemble:** Soft voting aggregation combining predicted class probability distributions across all 4 base models.

---

## 8. Web Application Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Landing page with system overview, workflow steps, and model cards |
| `/assessment` | GET | Interactive 4-section assessment form with demo presets and BMI tool |
| `/predict` | POST | Submits patient assessment form, returns multi-model risk classification |
| `/models` | GET | Model comparison dashboard with dynamic metrics table and visual plots |
| `/about` | GET | System documentation, feature definitions, and ML methodology |

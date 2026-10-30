@echo off
TITLE Smart Disease Risk Prediction System
COLOR 0A

echo ======================================================================
echo          SMART DISEASE RISK PREDICTION SYSTEM (RUNNER)
echo ======================================================================
echo.

IF NOT EXIST "venv\Scripts\activate.bat" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Checking dependencies...
pip install -r requirements.txt --quiet

IF NOT EXIST "data\disease_data.csv" (
    echo [*] Generating disease dataset...
    python src\generate_dataset.py
)

IF NOT EXIST "models\ensemble.pkl" (
    echo [*] Training models and generating evaluation artifacts...
    python src\train_models.py
)

echo.
echo ======================================================================
echo  Launching Flask Web Server at http://127.0.0.1:5000
echo  Press CTRL+C to stop the server
echo ======================================================================
echo.

python app.py
pause

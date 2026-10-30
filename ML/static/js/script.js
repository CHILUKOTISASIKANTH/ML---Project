/**
 * Smart Disease Risk Prediction System
 * Client-side interactivity, validation, and demo presets
 */

document.addEventListener("DOMContentLoaded", function () {

  // ---------------------------------------------------------------------------
  // Demo Presets
  // ---------------------------------------------------------------------------

  const presets = {
    low: {
      age: 27,
      gender: "Female",
      blood_pressure: 112,
      heart_rate: 64,
      glucose: 88,
      cholesterol: 168,
      bmi: 21.2,
      smoking: "Never",
      physical_activity: "High",
      family_history: "No",
      heart_disease: "No",
    },
    high: {
      age: 65,
      gender: "Male",
      blood_pressure: 155,
      heart_rate: 90,
      glucose: 172,
      cholesterol: 252,
      bmi: 33.1,
      smoking: "Current",
      physical_activity: "Low",
      family_history: "Yes",
      heart_disease: "Yes",
    },
  };

  const btnLow   = document.getElementById("btn-preset-low");
  const btnHigh  = document.getElementById("btn-preset-high");
  const btnClear = document.getElementById("btn-preset-clear");
  const form     = document.getElementById("assessment-form");

  if (btnLow)   btnLow.addEventListener("click",   () => fillForm(presets.low));
  if (btnHigh)  btnHigh.addEventListener("click",  () => fillForm(presets.high));
  if (btnClear) btnClear.addEventListener("click", () => { if (form) form.reset(); });

  function fillForm(data) {
    for (const [key, value] of Object.entries(data)) {
      const el = document.getElementById(key);
      if (!el) continue;
      el.value = value;
      el.dispatchEvent(new Event("change"));
    }
  }

  // ---------------------------------------------------------------------------
  // BMI Calculator Toggle
  // ---------------------------------------------------------------------------

  const bmiToggle = document.getElementById("bmi-toggle");
  const bmiPanel  = document.getElementById("bmi-calc-panel");

  if (bmiToggle && bmiPanel) {
    bmiToggle.addEventListener("click", function () {
      const open = bmiPanel.style.display !== "none";
      bmiPanel.style.display = open ? "none" : "block";
      bmiToggle.textContent  = open ? "Calculate BMI" : "Hide Calculator";
    });
  }

  const calcBtn = document.getElementById("btn-calc-bmi");
  if (calcBtn) {
    calcBtn.addEventListener("click", function () {
      const heightCm = parseFloat(document.getElementById("calc-height")?.value);
      const weightKg = parseFloat(document.getElementById("calc-weight")?.value);
      const bmiField = document.getElementById("bmi");

      if (!heightCm || !weightKg || heightCm <= 0 || weightKg <= 0) {
        showInlineError("Please enter valid height (cm) and weight (kg).");
        return;
      }

      const heightM = heightCm / 100.0;
      const bmi     = (weightKg / (heightM * heightM)).toFixed(1);

      if (bmiField) {
        bmiField.value = bmi;
        bmiField.dispatchEvent(new Event("change"));
        // Flash highlight
        bmiField.style.borderColor = "#16a34a";
        setTimeout(() => { bmiField.style.borderColor = ""; }, 1800);
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Form Validation on Submit
  // ---------------------------------------------------------------------------

  if (form) {
    form.addEventListener("submit", function (e) {
      const errors = [];

      const age  = parseInt(document.getElementById("age")?.value);
      const bp   = parseFloat(document.getElementById("blood_pressure")?.value);
      const hr   = parseInt(document.getElementById("heart_rate")?.value);
      const gluc = parseFloat(document.getElementById("glucose")?.value);
      const chol = parseFloat(document.getElementById("cholesterol")?.value);
      const bmi  = parseFloat(document.getElementById("bmi")?.value);

      if (isNaN(age)  || age  < 1   || age  > 120) errors.push("Age must be between 1 and 120.");
      if (isNaN(bp)   || bp   < 50  || bp   > 260) errors.push("Systolic Blood Pressure must be between 50 and 260 mmHg.");
      if (isNaN(hr)   || hr   < 30  || hr   > 220) errors.push("Resting Heart Rate must be between 30 and 220 bpm.");
      if (isNaN(gluc) || gluc < 40  || gluc > 450) errors.push("Fasting Glucose must be between 40 and 450 mg/dL.");
      if (isNaN(chol) || chol < 80  || chol > 500) errors.push("Total Cholesterol must be between 80 and 500 mg/dL.");
      if (isNaN(bmi)  || bmi  < 10  || bmi  > 75)  errors.push("BMI must be between 10.0 and 75.0 kg/m².");

      if (errors.length > 0) {
        e.preventDefault();
        showInlineError(errors.join(" "));
        return;
      }

      // Disable submit button and show loading state
      const submitBtn = document.getElementById("submit-btn");
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Running prediction…";
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Utility: Simple inline error notification
  // ---------------------------------------------------------------------------

  function showInlineError(message) {
    let box = document.getElementById("inline-validation-error");
    if (!box) {
      box = document.createElement("div");
      box.id = "inline-validation-error";
      box.className = "alert alert-danger";
      box.style.marginTop = "1rem";
      if (form) form.insertBefore(box, form.firstChild);
    }
    box.textContent = message;
    box.scrollIntoView({ behavior: "smooth", block: "center" });
    setTimeout(() => { box.textContent = ""; }, 8000);
  }

});

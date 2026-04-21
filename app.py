import streamlit as st
import pandas as pd
import numpy as np
import pickle

# ─── Load model artifacts ────────────────────────────────────────────────────
try:
    model   = pickle.load(open("model.pkl",   "rb"))
    columns = pickle.load(open("columns.pkl", "rb"))
    scaler  = pickle.load(open("scaler.pkl",  "rb"))
except Exception as e:
    st.error(f"Error loading model artifacts: {e}")
    st.stop()

# ─── Helpers ─────────────────────────────────────────────────────────────────
# The model was trained with one-hot encoded categorical features.
# We need to map user-friendly input values to the correct one-hot columns.

JOB_SATISFACTION_MAP = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}

def build_input_row(job_satisfaction, monthly_income, years_at_company,
                    overtime_val, dept_val):
    """Build a single-row DataFrame matching the training columns."""
    # Start with all zeros
    row = pd.DataFrame([np.zeros(len(columns))], columns=columns)

    # ── Numeric columns (set directly) ──
    row["MonthlyIncome"]   = monthly_income
    row["YearsAtCompany"]  = years_at_company
    row["OverTime"]        = overtime_val
    row["Department"]      = dept_val

    # ── One-hot: JobSatisfaction ──
    js_label = JOB_SATISFACTION_MAP.get(job_satisfaction)
    js_col   = f"JobSatisfaction_{js_label}"
    if js_col in row.columns:
        row[js_col] = 1.0

    return row


# ─── App header ──────────────────────────────────────────────────────────────
st.title("💼 Employee Attrition Prediction")
st.write("Enter employee details to predict the likelihood of attrition:")

# ─── Input widgets ───────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    job_satisfaction = st.slider(
        "Job Satisfaction", 1, 4, value=2,
        help="1: Low, 2: Medium, 3: High, 4: Very High"
    )
    monthly_income   = st.number_input("Monthly Income ($)", 1000, 50000, value=5000)
    years_at_company = st.number_input("Years at Company",   0,    40,    value=5)

with col2:
    overtime   = st.selectbox("OverTime",   ["Yes", "No"])
    department = st.selectbox("Department", ["Sales", "Research & Development", "Human Resources"])

# Encode OverTime: Yes=1, No=0
overtime_val = 1 if overtime == "Yes" else 0

# Encode Department (LabelEncoder alphabetical order)
dept_map = {
    "Human Resources":        0,
    "Research & Development": 1,
    "Sales":                  2,
}
dept_val = dept_map[department]

# ─── Single prediction ───────────────────────────────────────────────────────
if st.button("Predict Attrition"):
    try:
        input_df = build_input_row(
            job_satisfaction, monthly_income, years_at_company,
            overtime_val, dept_val
        )

        # Scale with the same scaler used during training
        input_scaled = scaler.transform(input_df.astype(float))
        pred = model.predict(np.array(input_scaled))
        prob = model.predict_proba(np.array(input_scaled))

        st.divider()

        if pred[0] == 1:
            st.error("⚠️ Prediction: Employee likely to LEAVE")
        else:
            st.success("✅ Prediction: Employee likely to STAY")

        st.subheader("Prediction Probability")
        st.write(f"🟢 Stay Probability: {prob[0][0]*100:.2f}%")
        st.write(f"🔴 Leave Probability: {prob[0][1]*100:.2f}%")

        prob_df = pd.DataFrame(
            {"Outcome": ["Stay", "Leave"], "Probability": [prob[0][0], prob[0][1]]}
        )
        st.bar_chart(prob_df.set_index("Outcome"))

    except Exception as e:
        st.error(f"Prediction Error: {e}")

import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Load model and columns
try:
    model = pickle.load(open("model.pkl", "rb"))
    columns = pickle.load(open("columns.pkl", "rb"))
except Exception as e:
    st.error(f"Error loading model or columns: {e}")
    st.stop()

st.title("💼 Employee Attrition Prediction")

st.write("Enter employee details to predict the likelihood of attrition:")

# Inputs
col1, col2 = st.columns(2)

with col1:
    job_satisfaction = st.slider("Job Satisfaction", 1, 4, help="1: Low, 2: Medium, 3: High, 4: Very High")
    monthly_income = st.number_input("Monthly Income ($)", 1000, 50000, value=5000)
    years_at_company = st.number_input("Years at Company", 0, 40, value=5)

with col2:
    overtime = st.selectbox("OverTime", ["Yes", "No"])
    department = st.selectbox("Department", ["Sales", "Research & Development", "Human Resources"])

overtime_val = 1 if overtime == "Yes" else 0
dept_map = {
    "Sales": 0,
    "Research & Development": 1,
    "Human Resources": 2
}

dept_val = dept_map[department]

if st.button("Predict Attrition"):

    try:
        # Create empty dataframe with ALL training columns in correct order
        input_df = pd.DataFrame(columns=columns)
        input_df.loc[0] = 0  # Default all features to 0

        # Fill available values
        input_df['JobSatisfaction'] = job_satisfaction
        input_df['MonthlyIncome'] = monthly_income
        input_df['YearsAtCompany'] = years_at_company
        input_df['OverTime'] = overtime_val
        input_df['Department'] = dept_val

        # Predict
        # Using the model fitted with feature names helps avoid UserWarnings
        pred = model.predict(input_df)
        prob = model.predict_proba(input_df)

        st.divider()

        if pred[0] == 1:
            st.error("⚠️ Prediction: Employee likely to LEAVE")
        else:
            st.success("✅ Prediction: Employee likely to STAY")

        st.subheader("Prediction Probability")
        
        st.write(f"🟢 Stay Probability: {prob[0][0]*100:.2f}%")
        st.write(f"🔴 Leave Probability: {prob[0][1]*100:.2f}%")

        prob_df = pd.DataFrame({
            "Outcome": ["Stay", "Leave"],
            "Probability": [prob[0][0], prob[0][1]]
        })
        st.bar_chart(prob_df.set_index("Outcome"))

    except Exception as e:
        st.error(f"Prediction Error: {e}")
import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Load model and columns
model = pickle.load(open("model.pkl", "rb"))
columns = pickle.load(open("columns.pkl", "rb"))

st.title("💼 Employee Attrition Prediction")

st.write("Enter employee details:")

# Inputs
job_satisfaction = st.slider("Job Satisfaction", 1, 4)
monthly_income = st.number_input("Monthly Income", 1000, 50000)
years_at_company = st.number_input("Years at Company", 0, 40)
overtime = st.selectbox("OverTime", ["Yes", "No"])
department = st.selectbox("Department", ["Sales", "Research & Development", "Human Resources"])

overtime_val = 1 if overtime == "Yes" else 0
dept_map = {
    "Sales": 0,
    "Research & Development": 1,
    "Human Resources": 2
}

dept_val = dept_map[department]

if st.button("Predict"):

    try:
        # Create empty dataframe with ALL training columns
        input_df = pd.DataFrame(columns=columns)

        # Fill values
        input_df = pd.DataFrame(columns=columns)

        input_df.loc[0] = 0

        input_df['JobSatisfaction'] = job_satisfaction
        input_df['MonthlyIncome'] = monthly_income
        input_df['YearsAtCompany'] = years_at_company
        input_df['OverTime'] = overtime_val   # ✅ FIXED HERE 
        input_df['Department'] = dept_val
        # Predict
        pred = model.predict(input_df)
        prob = model.predict_proba(input_df)

        if pred[0] == 1:
            st.error("⚠️ Employee likely to LEAVE")
        else:
            st.success("✅ Employee likely to STAY")

        st.subheader("Prediction Probability")

        st.write(f"🟢 Stay Probability: {prob[0][0]*100:.2f}%")
        st.write(f"🔴 Leave Probability: {prob[0][1]*100:.2f}%")

        st.bar_chart(prob[0])
    except Exception as e:
        st.error(f"Error: {e}")
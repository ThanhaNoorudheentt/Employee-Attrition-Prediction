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

        # Add feature importance visualization
        st.subheader("Top 10 Feature Importances (Model Global)")
        if hasattr(model, 'coef_'):
            # For linear/logistic regression
            importances = model.coef_[0]
            feat_imp_df = pd.DataFrame({
                "Feature": columns,
                "Importance": importances
            })
            feat_imp_df['Abs_Importance'] = feat_imp_df['Importance'].abs()
            feat_imp_df = feat_imp_df.sort_values(by='Abs_Importance', ascending=False).head(10)
            st.bar_chart(feat_imp_df.set_index("Feature")['Importance'])
        elif hasattr(model, 'feature_importances_'):
            # For tree-based models
            importances = model.feature_importances_
            feat_imp_df = pd.DataFrame({
                "Feature": columns,
                "Importance": importances
            })
            feat_imp_df = feat_imp_df.sort_values(by='Importance', ascending=False).head(10)
            st.bar_chart(feat_imp_df.set_index("Feature"))

    except Exception as e:
        st.error(f"Prediction Error: {e}")

st.divider()

st.subheader("Batch Prediction via CSV")
uploaded_file = st.file_uploader("Upload a CSV file with employee data (must contain relevant columns):", type=["csv"])
if uploaded_file is not None:
    try:
        user_df = pd.read_csv(uploaded_file)
        
        # Provide defaults for any missing columns
        missing_cols = [c for c in columns if c not in user_df.columns]
        for c in missing_cols:
            user_df[c] = 0
            
        # Select and order columns as model expects
        model_inputs = user_df[columns]
        
        predictions = model.predict(model_inputs)
        user_df['Predicted_Attrition'] = ["Leave" if p == 1 else "Stay" for p in predictions]
        
        st.write("Prediction Results:")
        st.dataframe(user_df)
        
        csv_data = user_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Predictions",
            data=csv_data,
            file_name='attrition_predictions.csv',
            mime='text/csv',
        )
    except Exception as e:
        st.error(f"Error processing CSV: {e}")
# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1iRArfOEClbbNaWaAevl91y6AqTZFh56o
"""



import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Foot Pressure Grading + Risk Alerts", layout="wide")
st.title("🦶 Diabetic Foot Pressure Grading & Risk Monitoring")

uploaded_files = st.file_uploader("📤 Upload One or More CSV Files", type="csv", accept_multiple_files=True)

# Pressure grading function
def grade_pressure(value):
    if value < 30:
        return "Grade 1 (Low)"
    elif value < 70:
        return "Grade 2 (Moderate)"
    else:
        return "Grade 3 (High)"

# Grading + Risk Evaluation
def process_dataset(df):
    for sensor in ["Sensor1", "Sensor2", "Sensor3"]:
        df[f"{sensor}_Grade"] = df[sensor].apply(grade_pressure)

    df["Mean_Pressure"] = df[["Sensor1", "Sensor2", "Sensor3"]].mean(axis=1)
    df["Overall_Grade"] = df["Mean_Pressure"].apply(grade_pressure)
    return df

# Risk rule
def check_risk(row):
    high_grades = sum(row[f"{s}_Grade"] == "Grade 3 (High)" for s in ["Sensor1", "Sensor2", "Sensor3"])
    return row["Mean_Pressure"] >= 70 or high_grades >= 2

# Pie chart helper
def plot_pie(data, title):
    fig = px.pie(data, names=data.index, values=data.values, title=title, hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

# Trend chart
def plot_trend(df, patient_name):
    fig = px.line(df[["Sensor1", "Sensor2", "Sensor3"]],
                  labels={"index": "Sample", "value": "Pressure", "variable": "Sensor"},
                  title=f"📈 Pressure Trend - {patient_name}")
    st.plotly_chart(fig, use_container_width=True)

# Initialize risk alert log
risk_alerts = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(uploaded_file)
            name = uploaded_file.name
            st.subheader(f"📝 Patient File: {name}")

            if not {"Sensor1", "Sensor2", "Sensor3"}.issubset(df.columns):
                st.error("❌ Required columns missing in file.")
                continue

            result_df = process_dataset(df)

            # Show trend chart
            plot_trend(result_df, name)

            # Show data table
            st.dataframe(result_df, use_container_width=True)

            # Pie charts
            st.markdown("#### 📊 Grade Distributions")
            col1, col2 = st.columns(2)
            with col1:
                plot_pie(result_df["Sensor1_Grade"].value_counts(), f"{name} - Sensor1")
            with col2:
                plot_pie(result_df["Sensor2_Grade"].value_counts(), f"{name} - Sensor2")
            col3, col4 = st.columns(2)
            with col3:
                plot_pie(result_df["Sensor3_Grade"].value_counts(), f"{name} - Sensor3")
            with col4:
                plot_pie(result_df["Overall_Grade"].value_counts(), f"{name} - Overall Grade")

            # Risk detection
            risky_rows = result_df[result_df.apply(check_risk, axis=1)]
            if not risky_rows.empty:
                risk_alerts.append({"Patient": name, "High Risk Samples": len(risky_rows)})

            # Download option
            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(f"📥 Download Graded CSV - {name}", data=csv, file_name=f"graded_{name}", mime="text/csv")

        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {e}")

    # Show risk alert summary
    if risk_alerts:
        st.subheader("🚨 Patients at Risk")
        risk_df = pd.DataFrame(risk_alerts)
        st.dataframe(risk_df)
    else:
        st.success("✅ No high-risk patients detected.")
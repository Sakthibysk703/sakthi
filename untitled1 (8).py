# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZnLERPVMMBxVhSLFI09hNYhTxCp9Vval
"""



import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# Page config
st.set_page_config(page_title="Diabetic Foot Pressure Grading", layout="centered")
st.title("🦶 Diabetic Foot Pressure Grading (3-Sensor Dataset)")

# File uploader
uploaded_file = st.file_uploader("Upload pressure sensor data (.xlsx)", type=["xlsx"])

# Grading function
def grade_pressure(value):
    if value < 30:
        return "Grade 1 (Low)"
    elif value < 70:
        return "Grade 2 (Moderate)"
    else:
        return "Grade 3 (High)"

# Data processing
def process_data(df):
    for sensor in ["Sensor 1", "Sensor 2", "Sensor 3"]:
        df[f"{sensor}_Grade"] = df[sensor].apply(grade_pressure)
    df["Mean_Pressure"] = df[["Sensor 1", "Sensor 2", "Sensor 3"]].mean(axis=1)
    df["Overall_Grade"] = df["Mean_Pressure"].apply(grade_pressure)
    return df

# Foot pressure drawing
def draw_foot_pressure(sensor1, sensor2, sensor3, ax):
    max_val = 1023  # Adjust this if the sensor readings are scaled differently
    heel_intensity = sensor1 / max_val
    ball_intensity = sensor2 / max_val
    toe_intensity = sensor3 / max_val

    # Clear the current figure to animate
    ax.clear()

    foot_parts = {
        "Heel": (1, 1.5, heel_intensity),
        "Ball": (1, 3.5, ball_intensity),
        "Toe": (1, 5, toe_intensity),
    }

    for part, (x, y, intensity) in foot_parts.items():
        color = plt.cm.Reds(intensity)  # Color intensity based on pressure
        circle = plt.Circle((x, y), 0.8, color=color, ec='black', lw=1)
        ax.add_patch(circle)
        ax.text(x, y, part, ha='center', va='center', fontsize=10, color='black')

    ax.set_xlim(0, 2)
    ax.set_ylim(0, 6.5)
    ax.set_aspect('equal')
    ax.axis('off')  # Hide axes for better visualization

# Visualization charts
def plot_visuals(df):
    st.subheader("📈 Pressure Over Time")
    st.line_chart(df[["Sensor 1", "Sensor 2", "Sensor 3"]])

    st.subheader("📊 Mean Pressure Bar Chart")
    st.bar_chart(df["Mean_Pressure"])

    st.subheader("🥧 Grade Distribution")
    grade_counts = df["Overall_Grade"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(grade_counts, labels=grade_counts.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

# Main logic
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.write("📄 Raw Data:", df.head())

        required_cols = ["Sensor 1", "Sensor 2", "Sensor 3"]
        if all(col in df.columns for col in required_cols):
            processed_df = process_data(df)

            st.subheader("🩺 Grading Result")
            st.dataframe(processed_df)

            # Charts
            plot_visuals(processed_df)

            # Right foot pressure visualization (animation)
            if not processed_df.empty:
                last_sample = processed_df.iloc[-1]
                fig, ax = plt.subplots(figsize=(4, 7))  # Adjust size if needed

                st.subheader("🦶 Right Foot Pressure Map (Animated)")

                # Create an empty container for the animation
                container = st.empty()

                # Iterate through the data to animate the pressure map
                for i in range(len(processed_df)):
                    sample = processed_df.iloc[i]
                    draw_foot_pressure(
                        sensor1=sample["Sensor 1"],
                        sensor2=sample["Sensor 2"],
                        sensor3=sample["Sensor 3"],
                        ax=ax
                    )

                    # Display the figure in the container
                    container.pyplot(fig)
                    time.sleep(0.1)  # Adjust this for speed of animation

            # Download button
            output_file = "graded_output.xlsx"
            processed_df.to_excel(output_file, index=False)
            with open(output_file, "rb") as f:
                st.download_button("📥 Download Graded Excel", data=f, file_name="graded_output.xlsx")

        else:
            st.error("❌ Required columns: 'Sensor 1', 'Sensor 2', and 'Sensor 3'")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
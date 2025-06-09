import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("enhanced_student_habits_performance_dataset.csv")

df = load_data()

# Sidebar filters
st.sidebar.title("Filter Data")
selected_semester = st.sidebar.selectbox("Select Semester", sorted(df['semester'].unique()))
selected_major = st.sidebar.selectbox("Select Major", sorted(df['major'].unique()))
selected_gender = st.sidebar.selectbox("Select Gender", sorted(df['gender'].unique()))

# Apply filters
filtered_df = df[(df['semester'] == selected_semester) &
                 (df['major'] == selected_major) &
                 (df['gender'] == selected_gender)]

# Halaman 1: Ringkasan
st.title("🎓 Student Performance Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Average Exam Score", round(filtered_df['exam_score'].mean(), 2))
col2.metric("Average GPA", round(filtered_df['previous_gpa'].mean(), 2))
col3.metric("Avg Attendance %", f"{round(filtered_df['attendance_percentage'].mean(), 2)}%")

st.subheader("Academic Performance by Semester")
st.bar_chart(filtered_df.groupby('semester')['exam_score'].mean())

st.subheader("Study Hours vs Exam Score")
st.plotly_chart(px.scatter(filtered_df, x='study_hours_per_day', y='exam_score', trendline="ols"))

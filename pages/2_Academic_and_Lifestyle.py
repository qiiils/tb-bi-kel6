import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📚 Academic & Lifestyle")

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

# GPA vs Exam Score
st.subheader("GPA vs Exam Score")
st.plotly_chart(px.scatter(filtered_df, x='previous_gpa', y='exam_score', trendline="ols"))

# Part-time job & Tutoring
col1, col2 = st.columns(2)
col1.plotly_chart(px.box(filtered_df, x='part_time_job', y='exam_score', title="Part-Time Job vs Exam Score"))
col2.plotly_chart(px.box(filtered_df, x='access_to_tutoring', y='exam_score', title="Tutoring Access vs Exam Score"))

# Media Sosial & Screen Time
st.subheader("Social Media & Screen Time vs Exam Score")
col3, col4 = st.columns(2)
col3.plotly_chart(px.scatter(filtered_df, x='social_media_hours', y='exam_score', trendline="ols"))
col4.plotly_chart(px.scatter(filtered_df, x='screen_time', y='exam_score', trendline="ols"))

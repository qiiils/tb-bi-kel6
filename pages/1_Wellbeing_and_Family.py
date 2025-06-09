import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💤 Wellbeing & Family Factors")

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

# Visualisasi wellbeing
col1, col2 = st.columns(2)
col1.plotly_chart(px.histogram(filtered_df, x='sleep_hours', nbins=20, title="Sleep Hours Distribution"))
col2.plotly_chart(px.histogram(filtered_df, x='mental_health_rating', nbins=10, title="Mental Health Rating"))

# Visualisasi faktor keluarga
col3, col4 = st.columns(2)
col3.plotly_chart(px.pie(filtered_df, names='parental_education_level', title="Parental Education Level"))
col4.plotly_chart(px.pie(filtered_df, names='family_income_range', title="Family Income Range"))

st.subheader("Parental Support Level vs Exam Score")
st.plotly_chart(px.box(filtered_df, x='parental_support_level', y='exam_score'))

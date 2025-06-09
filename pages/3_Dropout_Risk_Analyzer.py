import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

st.title("📉 Dropout Risk Analyzer")

@st.cache_data
def load_data():
    df = pd.read_csv("enhanced_student_habits_performance_dataset.csv")
    df = df.copy()
    # Encode dropout risk untuk model klasifikasi
    df['dropout_risk_encoded'] = df['dropout_risk'].map({'Low': 0, 'Medium': 1, 'High': 2})
    return df

df = load_data()

# Fitur & target untuk model
features = [
    'study_hours_per_day',
    'sleep_hours',
    'stress_level',
    'exam_anxiety_score',
    'time_management_score',
    'mental_health_rating'
]
X = df[features]
y = df['dropout_risk_encoded']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluasi model
st.subheader("Model Evaluation")
y_pred = model.predict(X_test)
st.text(classification_report(y_test, y_pred, target_names=['Low', 'Medium', 'High']))

# Feature importance
st.subheader("Top Contributing Factors")
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=True)
fig = px.bar(importances, orientation='h', title='Feature Importance')
st.plotly_chart(fig)

# Simulasi prediksi
st.subheader("Simulate Dropout Risk Prediction")
input_data = {}
for feature in features:
    min_val = float(df[feature].min())
    max_val = float(df[feature].max())
    mean_val = float(df[feature].mean())
    input_data[feature] = st.slider(feature.replace('_', ' ').title(), min_val, max_val, mean_val)

input_df = pd.DataFrame([input_data])
prediction = model.predict(input_df)[0]
pred_label = {0: 'Low', 1: 'Medium', 2: 'High'}[prediction]

st.success(f"Predicted Dropout Risk: **{pred_label}**")

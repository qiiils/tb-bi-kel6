import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import mysql.connector  # Impor konektor MySQL

# --- Konfigurasi ---
CSV_FILE_PATH = 'enhanced_student_habits_performance_dataset.csv'

# Konfigurasi MySQL
MYSQL_USER = 'root'
MYSQL_PASSWORD = '' 
MYSQL_HOST = 'localhost'    
MYSQL_PORT = 3306           
MYSQL_DB_NAME = 'academic_performance_dwh'

DATABASE_URL = f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}'

# --- FASE 1: EXTRACT ---
def extract_data(file_path):
    """
    Ekstraksi data mentah dari file CSV.
    Ini merepresentasikan langkah "Staging Area" di memori.
    """
    print(f"Mengambil data dari: {file_path}")
    try:
        df = pd.read_csv(file_path, delimiter=';')

        print(f"Data berhasil diekstrak. Jumlah baris: {len(df)}")
        print("Kolom yang tersedia di dataset (setelah perbaikan delimiter):")
        print(df.columns.tolist())
        
        return df
    except FileNotFoundError:
        print(f"Error: File tidak ditemukan di {file_path}")
        return None
    except Exception as e:
        print(f"Error saat mengekstrak data: {e}")
        return None

# --- FASE 2: TRANSFORM ---
def transform_data(df_raw):
    """
    Melakukan pembersihan, transformasi, dan pembentukan dimensi serta fakta.
    """
    print("Memulai proses transformasi data...")

    # --- Pembersihan Data Awal ---
    # 1. Menghapus duplikat berdasarkan student_id (asumsi student_id unik per observasi)
    df = df_raw.drop_duplicates(subset=['student_id']).copy()
    print(f"Jumlah baris setelah menghapus duplikat: {len(df)}")

    # 2. Menangani nilai hilang dan memastikan tipe data numerik
    for col in ['gender', 'major', 'diet_quality', 'exercise_frequency', 'parental_education_level',
                'internet_quality', 'extracurricular_participation', 'semester',
                'study_environment', 'access_to_tutoring', 'family_income_range',
                'parental_support_level', 'motivation_level', 'learning_style', 'social_activity']:
        if df[col].isnull().any():
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)
            print(f"Mengisi nilai hilang di '{col}' dengan modus.")

    numerical_cols = ['age', 'study_hours_per_day', 'social_media_hours', 'netflix_hours',
                      'attendance_percentage', 'sleep_hours', 'mental_health_rating',
                      'previous_gpa', 'stress_level', 'dropout_risk', 'screen_time',
                      'exam_anxiety_score', 'time_management_score', 'exam_score']
    
    for col in numerical_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce') 
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"Mengisi nilai hilang di '{col}' dengan median: {median_val}")

    df['gender'] = df['gender'].str.lower().replace({'m': 'male', 'f': 'female'})
    df['part_time_job'] = df['part_time_job'].replace({0: 'No', 1: 'Yes'})

    # --- Derivasi Atribut dan Pembuatan Dimensi ---
    dim_student_df = df[['student_id', 'age', 'gender', 'major', 'previous_gpa']].drop_duplicates().copy()
    dim_student_df['age_group'] = pd.cut(dim_student_df['age'], bins=[17, 20, 23, 100], labels=['18-20', '21-23', '>23'])
    dim_student_df.drop('age', axis=1, inplace=True) 
    dim_student_df['student_key'] = range(1, len(dim_student_df) + 1)

    dim_time_df = df[['semester']].drop_duplicates().copy()
    dim_time_df['year'] = dim_time_df['semester'].astype(str).apply(lambda x: int(x.split(' ')[1]) if len(x.split(' ')) > 1 else 2024)
    dim_time_df['academic_year'] = dim_time_df['year'].astype(str) + '/' + (dim_time_df['year'] + 1).astype(str)
    dim_time_df['time_key'] = range(1, len(dim_time_df) + 1)

    # --- Membuat tabel dimensi lainnya ---
    # Tambahkan kode untuk dim_study_habits_df, dim_socioeconomic_df, dll

    # --- Membuat Tabel Fakta ---
    fact_df = df.copy()

    # Merge dengan dimensi untuk mendapatkan Foreign Keys
    fact_df = fact_df.merge(dim_student_df[['student_id', 'student_key']], on='student_id', how='left')
    fact_df = fact_df.merge(dim_time_df[['semester', 'time_key']], on='semester', how='left')

    fact_academic_performance_df = fact_df[['student_key', 'time_key', 'exam_score', 'attendance_percentage', 'dropout_risk']].copy()
    fact_academic_performance_df['academic_performance_key'] = range(1, len(fact_academic_performance_df) + 1)

    return dim_student_df, dim_time_df, fact_academic_performance_df

# --- FASE 3: LOAD ---
def load_data(dim_student, dim_time, fact_academic_performance):
    print("Memulai proses loading data ke Data Warehouse MySQL...")
    try:
        # Koneksi ke database
        engine = create_engine(DATABASE_URL)
        
        # Muat tabel dimensi
        dim_student.to_sql('Dim_Student', engine, if_exists='replace', index=False)
        print("Dim_Student loaded.")
        
        dim_time.to_sql('Dim_Time', engine, if_exists='replace', index=False)
        print("Dim_Time loaded.")
        
        # Muat tabel fakta
        fact_academic_performance.to_sql('Fact_Academic_Performance', engine, if_exists='replace', index=False)
        print("Fact_Academic_Performance loaded.")

        print("Data berhasil dimuat ke Data Warehouse MySQL!")
    except mysql.connector.Error as err:
        print(f"Error MySQL: {err}")
    except Exception as e:
        print(f"Error saat memuat data: {e}")

# --- Eksekusi Pipeline ETL ---
if __name__ == '__main__':
    raw_data_df = extract_data(CSV_FILE_PATH)

    if raw_data_df is not None:
        dim_student_df, dim_time_df, fact_academic_performance_df = transform_data(raw_data_df)
        load_data(dim_student_df, dim_time_df, fact_academic_performance_df)

import pandas as pd
import mysql.connector
from mysql.connector import Error
from config import db_config

# =====================
# 1️⃣ Load CSV
# =====================
csv_file = r"emp_master_info.csv"

try:
    # Comma-separated CSV (Changed from tab-delimited)
    df = pd.read_csv(csv_file, sep=',')
    
    # Required columns
    required_cols = ['Emp_Id', 'Emp_Name', 'Join_Date', 'Sub_Section', 'Section', 
                     'Gross_Salary', 'Designation', 'Category', 'Grade']
    
    # Check if all columns exist
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing columns in CSV: {missing_cols}")
        exit()

    df = df[required_cols]

    # Join_Date to datetime.date format
    df['Join_Date'] = pd.to_datetime(df['Join_Date']).dt.date
    
    # Gross_Salary numeric format (if any string)
    df['Gross_Salary'] = pd.to_numeric(df['Gross_Salary'], errors='coerce').fillna(0)

except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit()

# =====================
# 2️⃣ MySQL Connection
# =====================
try:
    conn = mysql.connector.connect(**db_config)

    if conn.is_connected():
        print(f"Successfully connected to MySQL database: {db_config['database']}")

    cursor = conn.cursor()

    # =====================
    # 3️⃣ Table Create (if not exists)
    # =====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        Emp_Id INT PRIMARY KEY,
        Emp_Name VARCHAR(255),
        Join_Date DATE,
        Sub_Section VARCHAR(100),
        Section VARCHAR(100),
        Gross_Salary DECIMAL(15,2),
        Designation VARCHAR(100),
        Category VARCHAR(50),
        Grade VARCHAR(50)
    )
    """)
    print("Table checked/created successfully")

    # =====================
    # 4️⃣ From CSV to Database
    # =====================
    # INSERT IGNORE used to prevent errors from duplicate Emp_Id
    sql = """
    INSERT IGNORE INTO employees (Emp_Id, Emp_Name, Join_Date, Sub_Section, Section, Gross_Salary, Designation, Category, Grade)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    count = 0
    for _, row in df.iterrows():
        cursor.execute(sql, (
            row['Emp_Id'],
            row['Emp_Name'],
            row['Join_Date'],
            row['Sub_Section'],
            row['Section'],
            row['Gross_Salary'],
            row['Designation'],
            row['Category'],
            row['Grade']
        ))
        if cursor.rowcount > 0:
            count += 1

    conn.commit()
    print(f"Success: {count} new employees imported.")
    print(f"Total rows processed: {len(df)}")

except Error as e:
    print("Error while connecting to MySQL:", e)

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("MySQL connection is closed")



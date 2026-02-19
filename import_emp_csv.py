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
    # 3️⃣ Table Create (if not exists) & Schema Update
    # =====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        Emp_Id INT PRIMARY KEY,
        Emp_Name VARCHAR(255),
        Join_Date DATE,
        Sub_Section VARCHAR(100),
        Section VARCHAR(100),
        Gross_Salary DECIMAL(15,2),
        Category VARCHAR(50),
        Grade VARCHAR(50),
        designation_id INT,
        FOREIGN KEY (designation_id) REFERENCES designations(id)
    )
    """)
    
    # Try to add designation_id column if it doesn't exist (in case table already exists)
    try:
        cursor.execute("ALTER TABLE employees ADD COLUMN designation_id INT")
        cursor.execute("ALTER TABLE employees ADD FOREIGN KEY (designation_id) REFERENCES designations(id)")
        print("Added designation_id column to existing table.")
    except mysql.connector.Error as err:
        if err.errno == 1060: # Column already exists
            pass
        else:
            print(f"Schema update info: {err}")

    # Fetch designations for lookup
    cursor.execute("SELECT id, designation FROM designations")
    desig_lookup = {d[1].strip().lower(): d[0] for d in cursor.fetchall()}
    print(f"Loaded {len(desig_lookup)} designations for mapping.")

    print("Table checked/created successfully")

    # =====================
    # 4️⃣ From CSV to Database
    # =====================
    # INSERT IGNORE used to prevent errors from duplicate Emp_Id
    # ON DUPLICATE KEY UPDATE used to update existing records with new designation_id
    sql = """
    INSERT INTO employees (Emp_Id, Emp_Name, Join_Date, Sub_Section, Section, Gross_Salary, Category, Grade, designation_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        Emp_Name=VALUES(Emp_Name),
        Join_Date=VALUES(Join_Date),
        Sub_Section=VALUES(Sub_Section),
        Section=VALUES(Section),
        Gross_Salary=VALUES(Gross_Salary),
        Category=VALUES(Category),
        Grade=VALUES(Grade),
        designation_id=VALUES(designation_id)
    """
    
    count = 0
    for _, row in df.iterrows():
        desig_name = str(row['Designation']).strip().lower()
        d_id = desig_lookup.get(desig_name)
        
        cursor.execute(sql, (
            row['Emp_Id'],
            row['Emp_Name'],
            row['Join_Date'],
            row['Sub_Section'],
            row['Section'],
            row['Gross_Salary'],
            row['Category'],
            row['Grade'],
            d_id
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



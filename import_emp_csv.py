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
        Gross_Salary DECIMAL(15,2),
        Category VARCHAR(50),
        Grade VARCHAR(50),
        designation_id INT,
        sub_section_id INT,
        FOREIGN KEY (designation_id) REFERENCES designations(id),
        FOREIGN KEY (sub_section_id) REFERENCES sub_sections(id)
    )
    """)
    
    # Schema Update for existing table
    try:
        cursor.execute("ALTER TABLE employees ADD COLUMN sub_section_id INT")
        cursor.execute("ALTER TABLE employees ADD FOREIGN KEY (sub_section_id) REFERENCES sub_sections(id)")
        print("Added sub_section_id column.")
    except mysql.connector.Error:
        pass

    # Fetch lookup data
    cursor.execute("SELECT id, designation FROM designations")
    desig_lookup = {d[1].strip().lower(): d[0] for d in cursor.fetchall()}
    
    cursor.execute("SELECT id, name FROM sections")
    section_lookup = {s[1].strip().lower(): s[0] for s in cursor.fetchall()}
    
    cursor.execute("SELECT id, name, section_id FROM sub_sections")
    subsection_lookup = {(ss[1].strip().lower(), ss[2]): ss[0] for ss in cursor.fetchall()}

    print(f"Lookups loaded: {len(desig_lookup)} desigs, {len(section_lookup)} sections.")

    # =====================
    # 4️⃣ From CSV to Database
    # =====================
    sql = """
    INSERT INTO employees (Emp_Id, Emp_Name, Join_Date, Gross_Salary, Category, Grade, designation_id, sub_section_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        Emp_Name=VALUES(Emp_Name),
        Join_Date=VALUES(Join_Date),
        Gross_Salary=VALUES(Gross_Salary),
        Category=VALUES(Category),
        Grade=VALUES(Grade),
        designation_id=VALUES(designation_id),
        sub_section_id=VALUES(sub_section_id)
    """
    
    count = 0
    for _, row in df.iterrows():
        # 1. Designation Lookup
        desig_name = str(row['Designation']).strip().lower()
        d_id = desig_lookup.get(desig_name)
        
        # 2. Section/Sub-Section Lookup & Auto-creation
        sec_name = str(row['Section']).strip()
        sub_sec_name = str(row['Sub_Section']).strip()
        
        sec_key = sec_name.lower()
        if sec_key not in section_lookup:
            cursor.execute("INSERT INTO sections (name) VALUES (%s)", (sec_name,))
            s_id = cursor.lastrowid
            section_lookup[sec_key] = s_id
        else:
            s_id = section_lookup[sec_key]
            
        sub_key = (sub_sec_name.lower(), s_id)
        if sub_key not in subsection_lookup:
            cursor.execute("INSERT INTO sub_sections (name, section_id) VALUES (%s, %s)", (sub_sec_name, s_id))
            ss_id = cursor.lastrowid
            subsection_lookup[sub_key] = ss_id
        else:
            ss_id = subsection_lookup[sub_key]

        # 3. Insert Employee
        cursor.execute(sql, (
            row['Emp_Id'],
            row['Emp_Name'],
            row['Join_Date'],
            row['Gross_Salary'],
            row['Category'],
            row['Grade'],
            d_id,
            ss_id
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



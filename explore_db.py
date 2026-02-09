import mysql.connector
from config import db_config

def explore_db():
    try:
        config = db_config.copy()
        config['database'] = 'bio_time'
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        table = 'iclock_transaction'
        print(f"\n--- Structure of {table} ---")
        cursor.execute(f"DESCRIBE {table}")
        for col in cursor.fetchall():
            print(f"  {col[0]}: {col[1]}")
        
        print(f"\n--- Sample data from {table} ---")
        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
        columns = [i[0] for i in cursor.description]
        rows = cursor.fetchall()
        for row in rows:
            print(dict(zip(columns, row)))

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_db()



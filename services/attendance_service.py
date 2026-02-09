import mysql.connector
from config import biotime_config

def get_attendance_reports(report_date):
    """
    Fetches First In and Last Out times for all employees for a given date.
    :param report_date: string (YYYY-MM-DD)
    """
    conn = None
    try:
        conn = mysql.connector.connect(**biotime_config)
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            emp_code,
            MIN(punch_time) as in_time,
            MAX(punch_time) as out_time
        FROM iclock_transaction
        WHERE DATE(punch_time) = %s
        GROUP BY emp_code
        """
        
        cursor.execute(query, (report_date,))
        results = cursor.fetchall()

        # Process results to extract time only
        attendance_data = {}
        for row in results:
            attendance_data[row['emp_code']] = {
                'in_time': row['in_time'],
                'out_time': row['out_time']
            }
        
        return attendance_data

    except Exception as e:
        print(f"Error fetching attendance: {e}")
        return {}
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # Test with a date from our database exploration
    data = get_attendance_reports("2021-10-02")
    print(f"Total records found: {len(data)}")
    for ec, times in list(data.items())[:5]:
        print(f"Emp: {ec}, In: {times['in_time']}, Out: {times['out_time']}")

from app import create_app
from app.db import get_db

app = create_app()
with app.app_context():
    conn = get_db()
    cursor = conn.cursor()
    
    for table in ['Courses', 'Teaching', 'Enrollment', 'Sections', 'SectionItems', 'Assignments', 'Submissions']:
        print(f"--- {table} Table ---")
        try:
            cursor.execute(f"DESCRIBE {table}")
            for row in cursor.fetchall(): print(row)
        except Exception as e:
            print(f"Error describing {table}: {e}")
        print()
    
    conn.close()

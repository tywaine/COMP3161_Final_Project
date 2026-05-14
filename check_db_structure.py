from app import create_app
from app.db import get_db

app = create_app()
with app.app_context():
    conn = get_db()
    cursor = conn.cursor()
    
    print("--- Courses Table ---")
    cursor.execute("DESCRIBE Courses")
    for row in cursor.fetchall(): print(row)
    
    print("\n--- Teaching Table ---")
    cursor.execute("DESCRIBE Teaching")
    for row in cursor.fetchall(): print(row)
    
    print("\n--- Users Table ---")
    cursor.execute("DESCRIBE Users")
    for row in cursor.fetchall(): print(row)
    
    conn.close()

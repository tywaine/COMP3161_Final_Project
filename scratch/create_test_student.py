from app import create_app
from app.db import get_db, close_db

app = create_app()
with app.app_context():
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Check if course 7 exists
        cursor.execute("SELECT courseId FROM Courses WHERE courseId = 7")
        if not cursor.fetchone():
            print("Course 7 not found")
            exit(1)
            
        cursor.execute('INSERT INTO Users (userId, fullName, passwordHash, email, role) VALUES (400000001, "Test Student", "password123", "test@student.com", "student")')
        cursor.execute('INSERT INTO Students (userId, gpa) VALUES (400000001, 0.0)')
        cursor.execute('INSERT INTO Enrollment (studentId, courseId) VALUES (400000001, 7)')
        conn.commit()
        print("Test student created and enrolled in course 7")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_db(conn, cursor)

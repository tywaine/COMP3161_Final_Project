from app import create_app
from app.db import get_db, close_db
import json
from decimal import Decimal
from datetime import datetime

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, obj)

app = create_app()
with app.app_context():
    student_id = 300000003
    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute(
            """
            SELECT
                c.courseId,
                c.courseCode,
                c.courseName,
                c.description,
                c.createdByAdminId,
                DATE_FORMAT(c.createdAt, '%%Y-%%m-%%d %%H:%%i:%%s') AS createdAt,
                e.finalGrade,
                t.lecturerId,
                u.fullName AS lecturerName
            FROM Enrollment e
            JOIN Courses c ON e.courseId = c.courseId
            LEFT JOIN Teaching t ON c.courseId = t.courseId
            LEFT JOIN Users u ON t.lecturerId = u.userId
            WHERE e.studentId = %s
            ORDER BY c.courseCode
            """,
            (student_id,)
        )
        courses = cursor.fetchall()
        print(f"Fetched {len(courses)} courses")
        # Try to jsonify
        output = json.dumps({"courses": courses}, cls=ComplexEncoder)
        print("Success! JSON length:", len(output))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_db(connection, cursor)

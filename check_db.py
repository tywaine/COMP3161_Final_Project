from app import create_app
from app.db import get_db

app = create_app()
with app.app_context():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                c.courseCode,
                c.courseName,
                c.description,
                c.createdByAdminId,
                DATE_FORMAT(c.createdAt, '%%Y-%m-%d %H:%%i:%%s') AS createdAt,
                t.lecturerId,
                u.fullName AS lecturerName
            FROM Courses c
            LEFT JOIN Teaching t ON c.courseCode = t.courseCode
            LEFT JOIN Users u ON t.lecturerId = u.userId
            ORDER BY c.courseCode
        """
        cursor.execute(query)
        courses = cursor.fetchall()
        print(f'Successfully fetched {len(courses)} courses via route query')
        conn.close()
    except Exception as e:
        print(f'Query failed: {e}')

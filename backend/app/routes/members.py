from flask import Blueprint
from flask_jwt_extended import jwt_required
from mysql.connector import Error

from backend.app.db import get_db, close_db
from backend.app.utils.response import error_response, success_response

members_bp = Blueprint("members", __name__, url_prefix="/api/members")


@members_bp.route("/<string:course_code>", methods=["GET"])
@jwt_required()
def get_course_members(course_code: str):
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        course_code = course_code.upper().strip()

        # Check if course exists
        cursor.execute(
            """
            SELECT courseCode, courseName, description
            FROM Courses
            WHERE courseCode = %s
            """,
            (course_code,)
        )
        course = cursor.fetchone()

        if not course:
            return error_response("Course not found", 404)

        # Lecturer for the course
        cursor.execute(
            """
            SELECT
                u.userId,
                u.fullName,
                u.email,
                'lecturer' AS role
            FROM Users u
            JOIN Teaching t ON u.userId = t.lecturerId
            WHERE t.courseCode = %s
            """,
            (course_code,)
        )
        lecturer = cursor.fetchone()

        # Students in the course
        cursor.execute(
            """
            SELECT
                u.userId,
                u.fullName,
                u.email,
                'student' AS role,
                e.finalGrade
            FROM Users u
            JOIN Enrollment e ON u.userId = e.studentId
            WHERE e.courseCode = %s
            ORDER BY u.fullName
            """,
            (course_code,)
        )
        students = cursor.fetchall()

        # Convert Decimals
        for student in students:
            if student.get("finalGrade") is not None:
                student["finalGrade"] = float(student["finalGrade"])

        return success_response(
            "Course members retrieved successfully",
            {
                "course": course,
                "lecturer": lecturer,
                "students": students
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)
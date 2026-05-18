import re
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error
from datetime import datetime
from decimal import Decimal

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

courses_bp = Blueprint("courses", __name__, url_prefix="/api/courses")

def format_db_row(row):
    """Helper to convert database row values to JSON-serializable formats."""
    if not row:
        return row
    for key, value in row.items():
        if isinstance(value, datetime):
            row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, Decimal):
            row[key] = float(value)
    return row

@courses_bp.route("", methods=["POST"])
@jwt_required()
def create_course():
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        if current_role != "admin":
            return error_response("Only admins can create courses", 403)

        data = request.get_json()
        if not data:
            return error_response("Request body must be JSON")

        course_code = data.get("courseCode")
        course_name = data.get("courseName")
        description = data.get("description")
        lecturer_id = data.get("lecturerId")

        if not course_code or not course_name or not lecturer_id:
            return error_response("courseCode, courseName, and lecturerId are required")

        course_code = course_code.upper().strip()

        try:
            lecturer_id = int(lecturer_id)
        except (TypeError, ValueError):
            return error_response("lecturerId must be a number")

        if not re.fullmatch(r"[A-Z]{4}[0-3][0-9]{3}", course_code):
            return error_response(
                "courseCode must be 4 letters followed by 4 digits starting with 0-3, e.g. BIOL1000"
            )

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT courseCode FROM Courses WHERE courseCode = %s",
            (course_code,)
        )
        if cursor.fetchone():
            return error_response("courseCode already exists", 409)

        cursor.execute(
            "SELECT userId FROM Lecturers WHERE userId = %s",
            (lecturer_id,)
        )
        if not cursor.fetchone():
            return error_response("Lecturer not found", 404)

        cursor.execute(
            """
            SELECT COUNT(*) AS courseCount
            FROM Teaching
            WHERE lecturerId = %s
            """,
            (lecturer_id,)
        )
        course_count_result = cursor.fetchone()
        if course_count_result["courseCount"] >= 5:
            return error_response("Lecturer is already teaching 5 courses", 400)

        cursor.execute(
            """
            INSERT INTO Courses (courseCode, courseName, description, createdByAdminId)
            VALUES (%s, %s, %s, %s)
            """,
            (course_code, course_name, description, current_user_id)
        )

        cursor.execute(
            """
            INSERT INTO Teaching (lecturerId, courseCode)
            VALUES (%s, %s)
            """,
            (lecturer_id, course_code)
        )

        connection.commit()

        return success_response(
            "Course created successfully",
            {
                "course": {
                    "courseCode": course_code,
                    "courseName": course_name,
                    "description": description,
                    "lecturerId": lecturer_id,
                    "createdByAdminId": current_user_id
                }
            },
            201
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@courses_bp.route("", methods=["GET"])
@jwt_required()
def get_all_courses():
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                c.courseCode,
                c.courseName,
                c.description,
                c.createdByAdminId,
                c.createdAt,
                t.lecturerId,
                u.fullName AS lecturerName
            FROM Courses c
            LEFT JOIN Teaching t ON c.courseCode = t.courseCode
            LEFT JOIN Users u ON t.lecturerId = u.userId
            ORDER BY c.courseCode
            """
        )
        courses = [format_db_row(row) for row in cursor.fetchall()]

        return success_response("Courses retrieved successfully", {"courses": courses})

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@courses_bp.route("/student/<int:student_id>", methods=["GET"])
@jwt_required()
def get_courses_for_student(student_id):
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT userId FROM Students WHERE userId = %s",
            (student_id,)
        )
        if not cursor.fetchone():
            return error_response("Student not found", 404)

        cursor.execute(
            """
            SELECT
                c.courseCode,
                c.courseName,
                c.description,
                c.createdByAdminId,
                c.createdAt,
                e.finalGrade,
                t.lecturerId,
                u.fullName AS lecturerName
            FROM Enrollment e
            JOIN Courses c ON e.courseCode = c.courseCode
            LEFT JOIN Teaching t ON c.courseCode = t.courseCode
            LEFT JOIN Users u ON t.lecturerId = u.userId
            WHERE e.studentId = %s
            ORDER BY c.courseCode
            """,
            (student_id,)
        )
        courses = [format_db_row(row) for row in cursor.fetchall()]

        return success_response(
            f"Student courses for id# {student_id} retrieved successfully",
            {"courses": courses}
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@courses_bp.route("/lecturer/<int:lecturer_id>", methods=["GET"])
@jwt_required()
def get_courses_for_lecturer(lecturer_id):
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT userId FROM Lecturers WHERE userId = %s",
            (lecturer_id,)
        )
        if not cursor.fetchone():
            return error_response("Lecturer not found", 404)

        cursor.execute(
            """
            SELECT
                c.courseCode,
                c.courseName,
                c.description,
                c.createdByAdminId,
                c.createdAt,
                t.lecturerId
            FROM Teaching t
            JOIN Courses c ON t.courseCode = c.courseCode
            WHERE t.lecturerId = %s
            ORDER BY c.courseCode
            """,
            (lecturer_id,)
        )
        courses = [format_db_row(row) for row in cursor.fetchall()]

        return success_response(
            f"Lecturer courses for id# {lecturer_id} retrieved successfully",
            {"courses": courses}
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@courses_bp.route("/<string:course_code>/register", methods=["POST"])
@jwt_required()
def register_for_course(course_code: str):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        course_code = course_code.upper().strip()

        if current_role != "student":
            return error_response("Only students can register for courses", 403)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT userId FROM Students WHERE userId = %s",
            (current_user_id,)
        )
        if not cursor.fetchone():
            return error_response("Student not found", 404)

        cursor.execute(
            """
            SELECT courseCode, courseName
            FROM Courses
            WHERE courseCode = %s
            """,
            (course_code,)
        )
        course = cursor.fetchone()

        if not course:
            return error_response("Course not found", 404)

        cursor.execute(
            """
            SELECT studentId, courseCode
            FROM Enrollment
            WHERE studentId = %s AND courseCode = %s
            """,
            (current_user_id, course_code)
        )
        if cursor.fetchone():
            return error_response("Student is already registered for this course", 409)

        cursor.execute(
            """
            SELECT COUNT(*) AS courseCount
            FROM Enrollment
            WHERE studentId = %s
            """,
            (current_user_id,)
        )
        course_count_result = cursor.fetchone()

        if course_count_result["courseCount"] >= 6:
            return error_response("Student cannot register for more than 6 courses", 400)

        cursor.execute(
            """
            INSERT INTO Enrollment (studentId, courseCode)
            VALUES (%s, %s)
            """,
            (current_user_id, course_code)
        )

        connection.commit()

        return success_response(
            "Course registration successful",
            {
                "enrollment": {
                    "studentId": current_user_id,
                    "courseCode": course["courseCode"],
                    "courseName": course["courseName"]
                }
            },
            201
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)

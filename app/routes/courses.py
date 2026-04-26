import re
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

courses_bp = Blueprint("courses", __name__, url_prefix="/api/courses")


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
            return error_response(
                "courseCode, courseName, and lecturerId are required"
            )

        try:
            lecturer_id = int(lecturer_id)
        except (TypeError, ValueError):
            return error_response("lecturerId must be a number")

        if not re.fullmatch(r"[A-Z]{4}[0-3][0-9]{3}", course_code.upper()):
            return error_response("courseCode must be 4 letters followed by 4 digits starting with 0-3 (e.g. BIOL1000)")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Check if course code already exists
        cursor.execute("SELECT courseId FROM Courses WHERE courseCode = %s", (course_code,))
        existing_course = cursor.fetchone()
        if existing_course:
            return error_response("courseCode already exists", 409)

        # Check if lecturer exists
        cursor.execute("SELECT userId FROM Lecturers WHERE userId = %s", (lecturer_id,))
        lecturer = cursor.fetchone()
        if not lecturer:
            return error_response("Lecturer not found", 404)

        # Insert into Courses
        insert_course_sql = """
            INSERT INTO Courses (courseCode, courseName, description, createdByAdminId)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_course_sql, (
            course_code,
            course_name,
            description,
            current_user_id
        ))

        course_id = cursor.lastrowid

        # Insert into Teaching
        insert_teaching_sql = """
            INSERT INTO Teaching (lecturerId, courseId)
            VALUES (%s, %s)
        """
        cursor.execute(insert_teaching_sql, (lecturer_id, course_id))

        connection.commit()

        return success_response(
            "Course created successfully",
            {
                "course": {
                    "courseId": course_id,
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
        if connection:
            connection.rollback()
        return error_response("Database error", 500, e)

    except Exception as e:
        if connection:
            connection.rollback()
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

        get_courses_sql = """
            SELECT
                c.courseId,
                c.courseCode,
                c.courseName,
                c.description,
                c.createdByAdminId,
                c.createdAt,
                t.lecturerId,
                u.fullName AS lecturerName
            FROM Courses c
            LEFT JOIN Teaching t ON c.courseId = t.courseId
            LEFT JOIN Users u ON t.lecturerId = u.userId
            ORDER BY c.courseCode
        """
        cursor.execute(get_courses_sql)
        courses = cursor.fetchall()

        return success_response(
            "Courses retrieved successfully",
            {"courses": courses}
        )

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

        cursor.execute("SELECT userId FROM Students WHERE userId = %s", (student_id,))
        student = cursor.fetchone()
        if not student:
            return error_response("Student not found", 404)

        get_student_courses_sql = """
            SELECT
                c.courseId,
                c.courseCode,
                c.courseName,
                c.description,
                c.createdByAdminId,
                c.createdAt,
                e.finalGrade,
                t.lecturerId,
                u.fullName AS lecturerName
            FROM Enrollment e
            JOIN Courses c ON e.courseId = c.courseId
            LEFT JOIN Teaching t ON c.courseId = t.courseId
            LEFT JOIN Users u ON t.lecturerId = u.userId
            WHERE e.studentId = %s
            ORDER BY c.courseCode
        """
        cursor.execute(get_student_courses_sql, (student_id,))
        courses = cursor.fetchall()

        return success_response(
            f"Student courses for id# {student_id} retrieved successfully",
            {
                "courses": courses
            }
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

        cursor.execute("SELECT userId FROM Lecturers WHERE userId = %s", (lecturer_id,))
        lecturer = cursor.fetchone()
        if not lecturer:
            return error_response("Lecturer not found", 404)

        get_lecturer_courses_sql = """
            SELECT
                c.courseId,
                c.courseCode,
                c.courseName,
                c.description,
                c.createdByAdminId,
                c.createdAt,
                t.lecturerId
            FROM Teaching t
            JOIN Courses c ON t.courseId = c.courseId
            WHERE t.lecturerId = %s
            ORDER BY c.courseCode
        """
        cursor.execute(get_lecturer_courses_sql, (lecturer_id,))
        courses = cursor.fetchall()

        return success_response(
            f"Lecturer courses for id# {lecturer_id} retrieved successfully",
            {
                "courses": courses
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)
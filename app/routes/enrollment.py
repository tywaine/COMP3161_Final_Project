from flask import Blueprint, request
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

enrollment_bp = Blueprint("enrollment", __name__, url_prefix="/api/enrollment")


@enrollment_bp.route("/register", methods=["POST"])
def register_course():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        student_id = data.get("studentId")
        course_id = data.get("courseId")

        if not student_id or not course_id:
            return error_response("studentId and courseId are required")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO enrollments (student_id, course_id)
            VALUES (%s, %s)
        """, (student_id, course_id))

        connection.commit()

        return success_response("Student enrolled successfully")

    except Error as e:
        return error_response("Database error", 500, e)

    finally:
        close_db(connection, cursor)
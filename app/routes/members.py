from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

members_bp = Blueprint("members", __name__, url_prefix="/api/members")


@members_bp.route("/<int:course_id>", methods=["GET"])
def get_members(course_id):
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT u.user_id, u.username
            FROM users u
            JOIN enrollments e ON u.user_id = e.student_id
            WHERE e.course_id = %s
        """, (course_id,))
        students = cursor.fetchall()

        cursor.execute("""
            SELECT u.user_id, u.username
            FROM users u
            JOIN lecturer_course lc ON u.user_id = lc.lecturer_id
            WHERE lc.course_id = %s
        """, (course_id,))
        lecturer = cursor.fetchone()

        return success_response("Members retrieved", {
            "lecturer": lecturer,
            "students": students
        })

    except Error as e:
        return error_response("Database error", 500, e)

    finally:
        close_db(connection, cursor)
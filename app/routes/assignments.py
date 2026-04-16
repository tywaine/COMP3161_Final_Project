from flask import Blueprint, request
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

assignments_bp = Blueprint("assignments", __name__, url_prefix="/api/assignments")


@assignments_bp.route("/create", methods=["POST"])
def create_assignment():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        course_id = data.get("courseId")
        title = data.get("title")

        if not course_id or not title:
            return error_response("Missing fields")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO assignments (course_id, title)
            VALUES (%s, %s)
        """, (course_id, title))

        connection.commit()

        return success_response("Assignment created")

    except Error as e:
        return error_response("Database error", 500, e)

    finally:
        close_db(connection, cursor)
from flask import Blueprint, request
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

content_bp = Blueprint("content", __name__, url_prefix="/api/content")


@content_bp.route("/add", methods=["POST"])
def add_content():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        course_id = data.get("courseId")
        section = data.get("section")
        content = data.get("content")

        if not course_id or not content:
            return error_response("courseId and content required")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO course_content (course_id, section, content)
            VALUES (%s, %s, %s)
        """, (course_id, section, content))

        connection.commit()

        return success_response("Content added")

    except Error as e:
        return error_response("Database error", 500, e)

    finally:
        close_db(connection, cursor)